mod azure;

use azure::AzureQueueConfig;

use azure_storage_queues::prelude::*;
use std::sync::Arc;
use tokio::sync::Semaphore;
use tracing::{error, info};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load environment variables from .env file
    dotenv::dotenv().ok();
    // Initialize tracing
    tracing_subscriber::fmt::init();

    // Azure Queue configuration
    let azure_config = AzureQueueConfig::from_env()?;
    let queue_client = azure_config.create_queue_client();

    // Create semaphore to limit concurrent tasks (you can change this number)
    let semaphore = Arc::new(Semaphore::new(2)); // Set to 2 for your example

    info!(
        "Starting Azure Queue processor with max {} concurrent workers",
        2
    );

    loop {
        // Get messages from the queue (up to 32 messages at once)
        match queue_client
            .get_messages()
            .number_of_messages(32)
            .visibility_timeout(std::time::Duration::from_secs(60))
            .await
        {
            Ok(response) => {
                let messages = response.messages;

                if messages.is_empty() {
                    // No messages available, wait a bit before polling again
                    tokio::time::sleep(std::time::Duration::from_secs(5)).await;
                    continue;
                }

                info!("Received {} messages from queue", messages.len());

                // Process messages concurrently
                let mut tasks = Vec::new();

                for message in messages {
                    let semaphore = Arc::clone(&semaphore);
                    let queue_client = queue_client.clone();

                    let task = tokio::spawn(async move {
                        // Acquire semaphore permit (blocks if max threads are already running)
                        let _permit = semaphore.acquire().await.unwrap();

                        // Print the message data
                        println!("Thread processing - Message ID: {}", message.message_id);
                        println!("Thread processing - Message Text: {}", message.message_text);
                        println!("---");

                        // Delete the message after printing
                        let pop_receipt = PopReceipt::from(message.clone());
                        if let Err(e) = queue_client.pop_receipt_client(pop_receipt).delete().await
                        {
                            error!("Failed to delete message: {}", e);
                        }
                    });

                    tasks.push(task);
                }

                // Wait for all current batch of tasks to complete
                for task in tasks {
                    if let Err(e) = task.await {
                        error!("Task failed: {}", e);
                    }
                }
            }
            Err(e) => {
                error!("Failed to get messages from queue: {}", e);
                tokio::time::sleep(std::time::Duration::from_secs(10)).await;
            }
        }
    }
}