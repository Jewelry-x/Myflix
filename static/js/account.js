async function toggleForm() {
    var loginFields = document.getElementById('loginFields');
    var signupFields = document.getElementById('signupFields');
    var form = document.getElementById('form');

    if (loginFields.style.display === 'none') {
        // Switch to login form
        form.classList.toggle('fade');
        await new Promise(resolve => setTimeout(resolve, 1000));
        loginFields.style.display = 'block';
        signupFields.style.display = 'none';
        setTimeout(() => { form.classList.toggle('fade'); }, 250);
    } else {
        // Switch to signup form
        form.classList.toggle('fade');
        await new Promise(resolve => setTimeout(resolve, 1000));
        loginFields.style.display = 'none';
        signupFields.style.display = 'block';
        setTimeout(() => { form.classList.toggle('fade'); }, 250);
    }
}

var check = function () {
    if (document.getElementById('InputSignUpPassword').value ==
        document.getElementById('InputRepeatPassword').value) {
        document.getElementById('message').style.color = 'green';
        document.getElementById('message').innerHTML = '✅';
    } else {
        document.getElementById('message').style.color = 'red';
        document.getElementById('message').innerHTML = '❌';
    }
}

var handleSubmit = function (event) {
    var password = document.getElementById('InputLoginPassword').value;
    var confirm_password = document.getElementById('InputRepeatPassword').value;

    if (password !== confirm_password) {
        event.preventDefault(); // Prevent form submission
        alert('Passwords do not match. Please correct them.');
    }
}