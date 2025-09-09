// Initialize Mermaid when the page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof mermaid !== 'undefined') {
        // Detect if we're in dark mode
        const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        mermaid.initialize({
            startOnLoad: true,
            theme: isDarkMode ? 'dark' : 'default',
            themeVariables: {
                primaryColor: '#7D5699',
                primaryTextColor: isDarkMode ? '#ffffff' : '#3B464F',
                primaryBorderColor: isDarkMode ? '#555555' : '#D0D1E7',
                lineColor: isDarkMode ? '#ffffff' : '#3B464F',
                secondaryColor: isDarkMode ? '#444444' : '#F7C5C5',
                tertiaryColor: isDarkMode ? '#666666' : '#D0D1E7',
                background: isDarkMode ? '#1e1e1e' : '#ffffff',
                mainBkg: isDarkMode ? '#2d2d2d' : '#ffffff',
                secondBkg: isDarkMode ? '#3d3d3d' : '#f0f0f0',
                tertiaryBkg: isDarkMode ? '#4d4d4d' : '#e0e0e0'
            }
        });
        
        // Listen for theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                mermaid.initialize({
                    startOnLoad: true,
                    theme: e.matches ? 'dark' : 'default',
                    themeVariables: {
                        primaryColor: '#7D5699',
                        primaryTextColor: e.matches ? '#ffffff' : '#3B464F',
                        primaryBorderColor: e.matches ? '#555555' : '#D0D1E7',
                        lineColor: e.matches ? '#ffffff' : '#3B464F',
                        secondaryColor: e.matches ? '#444444' : '#F7C5C5',
                        tertiaryColor: e.matches ? '#666666' : '#D0D1E7',
                        background: e.matches ? '#1e1e1e' : '#ffffff',
                        mainBkg: e.matches ? '#2d2d2d' : '#ffffff',
                        secondBkg: e.matches ? '#3d3d3d' : '#f0f0f0',
                        tertiaryBkg: e.matches ? '#4d4d4d' : '#e0e0e0'
                    }
                });
                // Re-render all Mermaid diagrams
                mermaid.init();
            });
        }
    }
});

