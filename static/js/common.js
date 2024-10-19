'use strict';


// navbar variables
const nav = document.querySelector('.navbar-nav');
const navLinks = document.querySelectorAll('.nav-link');
const cartToggleBtn = document.querySelector('.shopping-cart-btn');
const navToggleBtn = document.querySelector('.menu-toggle-btn');



// nav toggle function
const navToggleFunc = function () {
  nav.classList.toggle('active');
  navToggleBtn.classList.toggle('active');
}

// shopping cart toggle function



// add event on nav-toggle-btn
navToggleBtn.addEventListener('click', function () {


  navToggleFunc();

});

// add event on all nav-link
for (let i = 0; i < navLinks.length; i++) {

  navLinks[i].addEventListener('click', navToggleFunc);

}