const registerForm =
    document.getElementById(
        "registerForm"
    );


const loginForm =
    document.getElementById(
        "loginForm"
    );

const registerPasswordToggle =
    document.getElementById(
        "registerPasswordToggle"
    );

if (registerPasswordToggle) {
    registerPasswordToggle.addEventListener("click", function () {
        const password = document.getElementById("registerPassword");
        const isVisible = password.type === "text";
        password.type = isVisible ? "password" : "text";
        registerPasswordToggle.setAttribute(
            "aria-label",
            isVisible ? "Show password" : "Hide password"
        );
    });
}


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();


            const fullName =
                document.getElementById(
                    "fullName"
                ).value.trim();


            const username =
                document.getElementById(
                    "registerUsername"
                ).value.trim();


            const email =
                document.getElementById(
                    "email"
                ).value.trim();


            const password =
                document.getElementById(
                    "registerPassword"
                ).value;


            const message =
                document.getElementById(
                    "registerMessage"
                );


            if (
                !fullName ||
                !username ||
                !email ||
                !password
            ) {

                message.textContent =
                    "Please fill all fields.";

                return;
            }


            const user = {

                fullName:
                    fullName,

                username:
                    username,

                email:
                    email,

                password:
                    password
            };


            localStorage.setItem(
                "aiScannerAccount",
                JSON.stringify(user)
            );


            message.textContent =
                "Registration successful. Redirecting...";


            setTimeout(
                function () {

                    window.location.href =
                        "login.html";

                },
                800
            );
        }
    );
}


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();


            const username =
                document.getElementById(
                    "username"
                ).value.trim();


            const password =
                document.getElementById(
                    "password"
                ).value;


            const message =
                document.getElementById(
                    "loginMessage"
                );


            const stored =
                localStorage.getItem(
                    "aiScannerAccount"
                );


            if (!stored) {

                message.textContent =
                    "No account found. Please register first.";

                return;
            }


            try {

                const account =
                    JSON.parse(stored);


                if (
                    account.username !==
                        username ||
                    account.password !==
                        password
                ) {

                    message.textContent =
                        "Invalid username or password.";

                    return;
                }


                localStorage.setItem(
                    "aiScannerUser",
                    JSON.stringify(account)
                );


                message.textContent =
                    "Login successful. Redirecting...";


                setTimeout(
                    function () {

                        window.location.href =
                            "dashboard.html";

                    },
                    500
                );


            } catch (error) {

                console.error(error);

                message.textContent =
                    "Unable to login.";
            }

        }
    );
}