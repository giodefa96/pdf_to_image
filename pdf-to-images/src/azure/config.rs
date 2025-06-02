use azure_storage::{CloudLocation, prelude::*};
use azure_storage_queues::{QueueServiceClientBuilder, QueueClient};
use tracing::info;

pub struct AzureQueueConfig {
    pub account_name: String,
    pub account_key: String,
    pub queue_name: String,
}

impl AzureQueueConfig {
    pub fn from_env() -> Result<Self, Box<dyn std::error::Error>> {
        let account_name = std::env::var("AZURE_STORAGE_ACCOUNT")
            .expect("AZURE_STORAGE_ACCOUNT environment variable must be set");
        let account_key = std::env::var("AZURE_STORAGE_ACCOUNT_KEY")
            .expect("AZURE_STORAGE_KEY environment variable must be set");
        let queue_name = std::env::var("AZURE_STORAGE_QUEUE_NAME")
            .unwrap_or_else(|_| "task-queue".to_string());

        Ok(Self {
            account_name,
            account_key,
            queue_name,
        })
    }

    pub fn create_queue_client(&self) -> QueueClient {
        info!("Using Azure Storage Account: {}", self.account_name);
        info!("Using Azure Storage Queue: {}", self.queue_name);
        info!("Using Azure Storage Key: {}", self.account_key);

        let storage_credentials = StorageCredentials::access_key(
            self.account_name.clone(), 
            self.account_key.clone()
        );
        
        let queue_service = QueueServiceClientBuilder::with_location(
            CloudLocation::Emulator {
                address: "127.0.0.1".to_string(),
                port: 10001, // Queue service port for Azurite
            },
            storage_credentials,
        )
        .build();
        
        queue_service.queue_client(&self.queue_name)
    }
}