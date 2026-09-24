(function () {

    const logoutLinks =
        document.querySelectorAll("#logoutLink");


    logoutLinks.forEach(function (link) {

        link.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                localStorage.removeItem(
                    "aiScannerUser"
                );

                sessionStorage.clear();

                window.location.href =
                    "login.html";
            }
        );
    });


    const userData =
        localStorage.getItem(
            "aiScannerUser"
        );


    if (userData) {

        try {

            const user =
                JSON.parse(userData);


            const usernameElements =
                document.querySelectorAll(
                    "#dashboardUsername"
                );


            usernameElements.forEach(
                function (element) {

                    element.textContent =
                        user.username ||
                        user.fullName ||
                        "User";
                }
            );


            const profileName =
                document.getElementById(
                    "profileName"
                );

            const profileUsername =
                document.getElementById(
                    "profileUsername"
                );

            const profileEmail =
                document.getElementById(
                    "profileEmail"
                );

            const profileAvatar =
                document.getElementById(
                    "profileAvatar"
                );

            const profileSummaryEmail =
                document.getElementById(
                    "profileSummaryEmail"
                );

            const profileFullName =
                document.getElementById(
                    "profileFullName"
                );

            const profileUsernameInput =
                document.getElementById(
                    "profileUsernameInput"
                );

            const profileEmailInput =
                document.getElementById(
                    "profileEmailInput"
                );


            if (profileName) {

                profileName.textContent =
                    user.fullName ||
                    "User";
            }


            if (profileUsername) {

                profileUsername.textContent =
                    user.username ||
                    "-";
            }


            if (profileEmail) {

                profileEmail.textContent =
                    user.email ||
                    "-";
            }

            if (profileAvatar) {
                profileAvatar.textContent = (
                    user.fullName || user.username || "U"
                ).charAt(0).toUpperCase();
            }

            if (profileSummaryEmail) {
                profileSummaryEmail.textContent = user.email || "-";
            }

            if (profileFullName) {
                profileFullName.value = user.fullName || "";
            }

            if (profileUsernameInput) {
                profileUsernameInput.value = user.username || "";
            }

            if (profileEmailInput) {
                profileEmailInput.value = user.email || "";
            }

        } catch (error) {

            console.error(
                "User data error:",
                error
            );
        }
    }

    const profileForm = document.getElementById("profileForm");

    if (profileForm) {
        profileForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const storedAccount = localStorage.getItem("aiScannerAccount");
            const storedUser = localStorage.getItem("aiScannerUser");
            const account = storedAccount ? JSON.parse(storedAccount) : {};
            const user = storedUser ? JSON.parse(storedUser) : {};
            const password = document.getElementById("profilePassword").value;

            const updatedUser = {
                ...account,
                ...user,
                fullName: document.getElementById("profileFullName").value.trim(),
                username: document.getElementById("profileUsernameInput").value.trim(),
                email: document.getElementById("profileEmailInput").value.trim()
            };

            if (password) {
                updatedUser.password = password;
            }

            localStorage.setItem("aiScannerAccount", JSON.stringify(updatedUser));
            localStorage.setItem("aiScannerUser", JSON.stringify(updatedUser));

            document.getElementById("profileMessage").textContent =
                "Profile updated successfully.";
        });
    }

})();