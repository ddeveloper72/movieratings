function toggleMobileNav() {
    const mainNav = document.getElementById('mobile-menu');
    if (mainNav.className === 'navbar__nav') {
      mainNav.className = 'navbar__mobile';
    } else {
      mainNav.className = 'navbar__nav';
    }
  }