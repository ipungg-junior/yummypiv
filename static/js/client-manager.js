class CookieManager {
    // Method to set a cookie with a specific name, value, and expiration in hours
    static setCookie(name, value, hours) {
        const expirationDate = new Date();
        expirationDate.setTime(expirationDate.getTime() + (hours * 60 * 60 * 1000));
        const expires = "expires=" + expirationDate.toUTCString();
        document.cookie = `${name}=${encodeURIComponent(value)}; ${expires}; path=/`;
    }

    // Method to get a cookie by its name
    static getCookie(name) {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            let [cookieName, cookieValue] = cookie.split("=");
            if (cookieName === name) {
                return decodeURIComponent(cookieValue);
            }
        }
        return null; // Return null if the cookie is not found
    }
}

