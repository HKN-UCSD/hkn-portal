let user = null;

export let fetchSelf = async () => {
    if (user === null) {
        let response = await fetch(`/api/users/self/`);
        let userData = await response.json();
        return userData;
    }
    
    return user;
}

export let getCsrfToken = () => document.cookie
        .split("; ")
        .find((element) => element.startsWith("csrftoken="))
        .split("=")[1];

export let csrfSafeReq = (method, body) => {
    return {
        method: method,
        headers: {"X-CSRFToken": getCsrfToken(), "Content-Type": "application/json"},
        body: body
    }
}
