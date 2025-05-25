// Esporta i moduli interni
mod pdf_to_image;

// Re-esporta le funzionalità pubbliche per un utilizzo più semplice
pub use pdf_to_image::convert_pdf_to_images;