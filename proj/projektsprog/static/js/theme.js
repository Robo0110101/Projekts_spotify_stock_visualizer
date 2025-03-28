function toggleTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = themeToggle.checked ? 'dark' : 'light';
    document.body.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
}

function toggleSettings() {
    const dropdown = document.getElementById('settingsDropdown');
    dropdown.classList.toggle('show-settings');
}

window.onclick = function(event) {
    if (!event.target.matches('.settings-btn')) {
        const dropdowns = document.getElementsByClassName("settings-dropdown");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show-settings')) {
                openDropdown.classList.remove('show-settings');
            }
        }
    }
}