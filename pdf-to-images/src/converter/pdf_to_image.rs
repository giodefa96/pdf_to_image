use pdf2image::{image, PDF2ImageError, RenderOptionsBuilder, PDF};
use std::path::Path;

pub fn convert_pdf_to_images(
    pdf_path: &str,
    output_dir: &str
) -> Result<(), PDF2ImageError> {
    // Carica il PDF
    let pdf = PDF::from_file(pdf_path)?;
    let num_pages = pdf.page_count();
    
    // Renderizza le pagine
    let pages = pdf.render(
        pdf2image::Pages::Range(1..=num_pages),
        RenderOptionsBuilder::default().pdftocairo(true).build()?,
    )?;

    // Crea la directory di output se non esiste
    match std::fs::create_dir(output_dir) {
        Ok(_) => {},
        Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {
            eprintln!("Output directory already exists, proceeding with saving images.");
        },
        Err(e) => {
            eprintln!("Failed to create output directory: {}", e);
            return Err(PDF2ImageError::from(e));
        }
    }
    
    // Salva le immagini
    for (i, page) in pages.iter().enumerate() {
        let output_path = format!("{}/{}.jpg", output_dir, i + 1);
        page.save_with_format(output_path, image::ImageFormat::Jpeg)?;
    }

    Ok(())
}

// Puoi aggiungere altre funzioni correlate alla conversione PDF qui