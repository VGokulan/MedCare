document.addEventListener("DOMContentLoaded", () => {
  // These are the only elements the script needs for the login page.
  const container = document.getElementById("container");
  const registerBtn = document.getElementById("register");
  const loginBtn = document.getElementById("login");

  // This adds the '.active' class to the container when "Admin Login" is clicked.
  // This triggers the CSS animation.
  if (registerBtn) {
    registerBtn.addEventListener("click", () => {
      if (container) {
        container.classList.add("active");
      }
    });
  }

  // This removes the '.active' class when "User Login" is clicked.
  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      if (container) {
        container.classList.remove("active");
      }
    });
  }

  // A reusable function to show/hide the password.
  function setupPasswordToggle(inputId, toggleId) {
    const passwordInput = document.getElementById(inputId);
    const togglePassword = document.getElementById(toggleId);

    // This check prevents errors if an element isn't found.
    if (passwordInput && togglePassword) {
      togglePassword.addEventListener("click", function () {
        const type =
          passwordInput.getAttribute("type") === "password"
            ? "text"
            : "password";
        passwordInput.setAttribute("type", type);

        // This correctly toggles the eye icon.
        this.querySelector("i").classList.toggle("fa-eye");
        this.querySelector("i").classList.toggle("fa-eye-slash");
      });
    }
  }

  // We only call the function for the two password fields that exist on login.html.
  setupPasswordToggle("user-password", "toggle-user-password");
  setupPasswordToggle("admin-password", "toggle-admin-password");
});
