// Dichiara il modulo converter
mod converter;

use pdf2image::PDF2ImageError;

fn main() -> Result<(), PDF2ImageError> {
    // Utilizza la funzione dalla libreria
    converter::convert_pdf_to_images("examples/pdfs/test.pdf", "examples/out")?;
    
    Ok(())
}