document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {

        const downloadBtn = document.getElementById('download-btn');
            if (downloadBtn) {
                downloadBtn.addEventListener('click', function () {
                    setTimeout(() => {
                        const captureTarget = document.getElementById('layout');

                        // Désactiver temporairement le zoom et le défilement pour éviter les interférences
                        const originalZoom = document.body.style.zoom;
                        const originalOverflow = document.body.style.overflow;
                        document.body.style.zoom = 1;
                        document.body.style.overflow = 'hidden';

                        html2canvas(captureTarget, {
                            scale: 2, // Facteur d'échelle constant pour une qualité optimale
                            width: 1920, // Largeur fixe
                            height: 1400, // Hauteur fixe
                            windowWidth: 1920, // Simulation d'une fenêtre de 1920px de large
                            windowHeight: 1400, // Simulation d'une fenêtre de 1180px de haut
                            useCORS: true, // Pour supporter les images externes
                            logging: false, // Désactiver les logs pour les performances
                            scrollX: 0,
                            scrollY: 0
                        }).then(canvas => {
                            const link = document.createElement('a');
                            link.download = 'screenshot.png';
                            link.href = canvas.toDataURL();
                            link.click();

                            // Restaurer les styles d'origine
                            document.body.style.zoom = originalZoom;
                            document.body.style.overflow = originalOverflow;
                        }).catch(error => {
                            console.error("Erreur lors de la capture :", error);
                            document.body.style.zoom = originalZoom;
                            document.body.style.overflow = originalOverflow;
                        });
                    }, 1000);
                });
            } else {
            console.error("Element with ID 'download-btn' not found.");
        }
    }, 1000); // Wait 1 secs
});
