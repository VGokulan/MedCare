

        const container = document.getElementById('container');
        const loginBtn = document.getElementById('login');
        const registerBtn = document.getElementById('register');
        const forgotPasswordLink = document.getElementById('forgot-password-link');
        const adminForgotPasswordLink = document.getElementById('admin-forgot-password-link');
        const signupLink = document.getElementById('signup-link');
        const backToLogin = document.getElementById('back-to-login');
        const backToAdminLogin = document.getElementById('back-to-admin-login');
        const backToLoginFromSignup = document.getElementById('back-to-login-from-signup');

        // Password visibility toggle function
        function setupPasswordToggle(passwordId, toggleId) {
            const passwordField = document.getElementById(passwordId);
            const toggleButton = document.getElementById(toggleId);
            
            toggleButton.addEventListener('click', function() {
                if (passwordField.type === 'password') {
                    passwordField.type = 'text';
                    toggleButton.innerHTML = '<i class="far fa-eye-slash"></i>';
                } else {
                    passwordField.type = 'password';
                    toggleButton.innerHTML = '<i class="far fa-eye"></i>';
                }
            });
        }

        // Setup password toggles for all password fields
        setupPasswordToggle('user-password', 'toggle-user-password');
        setupPasswordToggle('admin-password', 'toggle-admin-password');
        setupPasswordToggle('signup-password', 'toggle-signup-password');
        setupPasswordToggle('confirm-password', 'toggle-confirm-password');

        // Initially show user login
        container.classList.remove('active');
        container.classList.remove('show-forgot');
        container.classList.remove('show-signup');
        container.classList.remove('show-admin-forgot');

        // Toggle between user and admin login
        registerBtn.addEventListener('click', () => {
            container.classList.add('active');
            container.classList.remove('show-forgot');
            container.classList.remove('show-signup');
            container.classList.remove('show-admin-forgot');
        });

        loginBtn.addEventListener('click', () => {
            container.classList.remove('active');
            container.classList.remove('show-forgot');
            container.classList.remove('show-signup');
            container.classList.remove('show-admin-forgot');
        });

        // Show forgot password form (user)
        forgotPasswordLink.addEventListener('click', (e) => {
            e.preventDefault();
            container.classList.remove('active');
            container.classList.add('show-forgot');
            container.classList.remove('show-signup');
            container.classList.remove('show-admin-forgot');
        });

        // Show forgot password form (admin)
        adminForgotPasswordLink.addEventListener('click', (e) => {
            e.preventDefault();
            container.classList.add('active');
            container.classList.remove('show-forgot');
            container.classList.remove('show-signup');
            container.classList.add('show-admin-forgot');
        });

        // Show signup form
        signupLink.addEventListener('click', (e) => {
            e.preventDefault();
            container.classList.remove('active');
            container.classList.remove('show-forgot');
            container.classList.add('show-signup');
            container.classList.remove('show-admin-forgot');
        });

        // Back to login from forgot password (user)
        backToLogin.addEventListener('click', (e) => {
            e.preventDefault();
            container.classList.remove('active');
            container.classList.remove('show-forgot');
            container.classList.remove('show-signup');
            container.classList.remove('show-admin-forgot');
        });

        // Back to login from forgot password (admin)
        backToAdminLogin.addEventListener('click', (e) => {
            e.preventDefault();
            container.classList.add('active');
            container.classList.remove('show-forgot');
            container.classList.remove('show-signup');
            container.classList.remove('show-admin-forgot');
        });

        // Back to login from signup
        backToLoginFromSignup.addEventListener('click', (e) => {
            e.preventDefault();
            container.classList.remove('active');
            container.classList.remove('show-forgot');
            container.classList.remove('show-signup');
            container.classList.remove('show-admin-forgot');
        });
