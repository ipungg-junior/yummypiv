class FetchManager {
    constructor(csrfToken, debug = true) {
        this.csrfToken = csrfToken;
        this.debug = debug; // Debug mode
    }

    post(url, formData) {
        return this.#fetchRequest(url, 'POST', formData);
    }

    #fetchRequest(url, method, body = null) {
        return fetch(url, {
            method: method,
            body: body,
            headers: {
                'X-CSRFToken': this.csrfToken,
            },
        })
        .then(response => this.#handleResponse(response))
        .catch(error => this.#handleError(error));
    }

    #handleResponse(response) {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Request failed with status ' + response.status);
        }
    }

    #handleError(error) {
        if (this.debug) {
            alert('Fetch error: ' + error.message); // Menampilkan alert jika debug true
        } else {
            console.log('Fetch error: ' + error.message); // Console log jika debug false
        }
    }
}