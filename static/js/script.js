'use strict';

/**
 * element toggle function
 */

const elemToggleFunc = function (elem) { elem.classList.toggle("active"); }



/**
 * header sticky & go to top
 */

const menuToggle = document.getElementById('mobile-menu');
const navLinks = document.getElementById('nav-links');
const navbarFloat = document.getElementById('navbar');

menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
});



window.addEventListener("scroll", function () {

  if (window.scrollY > 300) {
    navbarFloat.style.background = 'linear-gradient(45deg, #00000080, #00000021);'; // Ganti dengan warna yang diinginkan
} else {
    navbarFloat.style.background = 'var(--gradient-orange);'; // Kembali ke warna semula (atau warna default)
}

});

menuToggle.addEventListener("click", function () {

  elemToggleFunc(menuToggle);

});

/**
 * skills toggle
 */

const toggleBtnBox = document.querySelector("[data-toggle-box]");

for (let i = 0; i < toggleBtns.length; i++) {
  toggleBtns[i].addEventListener("click", function () {

    elemToggleFunc(toggleBtnBox);
    for (let i = 0; i < toggleBtns.length; i++) { elemToggleFunc(toggleBtns[i]); }
    elemToggleFunc(skillsBox);

  });
}

/**
 * check & apply last time selected theme from localStorage
 */
