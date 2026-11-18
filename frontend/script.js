
// ======================================
// BLUEWATCH - FRONTEND JAVASCRIPT
// ======================================

const API_URL = "http://127.0.0.1:8000";


// ======================================
// DISPLAY MESSAGES
// ======================================

function showMessage(text, type) {
    const message = document.getElementById("message");

    if (!message) return;

    message.textContent = text;
    message.className = "message " + type;
}


// ======================================
// PASSWORD SHOW / HIDE
// ======================================

function togglePassword(id, button) {
    const input = document.getElementById(id);

    if (!input || !button) return;

    if (input.type === "password") {
        input.type = "text";
        button.textContent = "Hide";
    } else {
        input.type = "password";
        button.textContent = "Show";
    }
}


// ======================================
// API REQUEST FUNCTION
// ======================================

async function apiRequest(endpoint, data) {
    let response;

    try {
        response = await fetch(`${API_URL}${endpoint}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
    } catch (error) {
        throw new Error(
            "Cannot connect to backend. Start FastAPI on port 8000."
        );
    }

    let result;

    try {
        result = await response.json();
    } catch {
        throw new Error("Invalid response received from backend.");
    }

    if (!response.ok) {
        throw new Error(
            typeof result.detail === "string"
                ? result.detail
                : "Something went wrong. Please try again."
        );
    }

    return result;
}


// ======================================
// SIGNUP API CONNECTION
// ======================================

const signupForm = document.getElementById("signupForm");

if (signupForm) {
    signupForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const fullName =
            document.getElementById("fullName").value.trim();

        const email =
            document.getElementById("email").value.trim();

        const password =
            document.getElementById("password").value;

        const confirmPassword =
            document.getElementById("confirmPassword").value;

        if (!fullName || !email || !password || !confirmPassword) {
            showMessage("Please fill in all fields.", "error");
            return;
        }

        if (fullName.length < 2) {
            showMessage("Please enter a valid full name.", "error");
            return;
        }

        if (password.length < 8 || password.length > 128) {
            showMessage(
                "Password must contain 8 to 128 characters.",
                "error"
            );
            return;
        }

        if (password !== confirmPassword) {
            showMessage("Passwords do not match.", "error");
            return;
        }

        const submitButton = signupForm.querySelector(
            'button[type="submit"]'
        );

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Creating Account...";
        }

        try {
            const result = await apiRequest("/api/signup", {
                full_name: fullName,
                email: email,
                password: password
            });

            showMessage(
                result.message ||
                "Account created successfully! Redirecting to login...",
                "success"
            );

            signupForm.reset();

            setTimeout(function() {
                window.location.href = "login.html";
            }, 1500);

        } catch (error) {
            showMessage(error.message, "error");

        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = "Create Account";
            }
        }
    });
}


// ======================================
// LOGIN API CONNECTION
// ======================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const email =
            document.getElementById("loginEmail").value.trim();

        const password =
            document.getElementById("loginPassword").value;

        if (!email || !password) {
            showMessage(
                "Please enter your email and password.",
                "error"
            );
            return;
        }

        const submitButton = loginForm.querySelector(
            'button[type="submit"]'
        );

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Logging In...";
        }

        try {
            const result = await apiRequest("/api/login", {
                email: email,
                password: password
            });

            if (!result.user) {
                throw new Error(
                    "User details were not returned by backend."
                );
            }

            sessionStorage.setItem(
                "bluewatchUser",
                JSON.stringify(result.user)
            );

            showMessage(
                "Login successful! Opening dashboard...",
                "success"
            );

            setTimeout(function() {
                window.location.href = "dashboard.html";
            }, 1000);

        } catch (error) {
            showMessage(error.message, "error");

        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = "Login";
            }
        }
    });
}


// ======================================
// GET LOGGED-IN USER DETAILS
// ======================================

function getLoggedInUser() {
    const userData = sessionStorage.getItem("bluewatchUser");

    if (!userData) {
        return null;
    }

    try {
        return JSON.parse(userData);
    } catch (error) {
        sessionStorage.removeItem("bluewatchUser");
        return null;
    }
}


// ======================================
// LOGOUT
// ======================================

function logout() {
    sessionStorage.removeItem("bluewatchUser");
    window.location.href = "index.html";
}


// ======================================
// DASHBOARD USER CHECK
// ======================================

document.addEventListener("DOMContentLoaded", function() {
    const user = getLoggedInUser();

    const welcomeElement =
        document.getElementById("welcomeUser");

    if (welcomeElement && !user) {
        window.location.href = "login.html";
        return;
    }

    if (user && welcomeElement) {
        welcomeElement.textContent =
            "Welcome, " + user.full_name + "!";
    }
});


// ======================================
// ML ECOSYSTEM PREDICTION
// ======================================

const MARINE_FIELDS = [
    "Region",
    "Season",
    "Weather",
    "Water_Temperature_C",
    "Salinity_PSU",
    "pH",
    "Dissolved_Oxygen_mg_L",
    "Wave_Height_m",
    "Current_Speed_m_s",
    "Chlorophyll_mg_m3",
    "Plastic_Pollution_Index",
    "Oil_Spill_Index",
    "Algae_Index",
    "Marine_Species",
    "Estimated_Population",
    "Biodiversity_Index"
];

const NUMERIC_FIELDS = [
    "Water_Temperature_C",
    "Salinity_PSU",
    "pH",
    "Dissolved_Oxygen_mg_L",
    "Wave_Height_m",
    "Current_Speed_m_s",
    "Chlorophyll_mg_m3",
    "Plastic_Pollution_Index",
    "Oil_Spill_Index",
    "Algae_Index",
    "Estimated_Population",
    "Biodiversity_Index"
];


// ======================================
// READ PREDICTION FORM VALUES
// ======================================

function getMarineInput(form) {
    const inputData = {};

    for (const field of MARINE_FIELDS) {
        const element = form.elements.namedItem(field);

        if (!element) {
            throw new Error(
                `Missing form field: ${field}. Check its name attribute in dashboard.html.`
            );
        }

        const value = element.value.trim();

        if (value === "") {
            throw new Error(
                `Please enter ${field.replaceAll("_", " ")}.`
            );
        }

        if (NUMERIC_FIELDS.includes(field)) {
            const numberValue = Number(value);

            if (!Number.isFinite(numberValue)) {
                throw new Error(
                    `Please enter a valid number for ${field}.`
                );
            }

            if (
                field === "Estimated_Population" &&
                (!Number.isInteger(numberValue) || numberValue < 0)
            ) {
                throw new Error(
                    "Estimated Population must be a non-negative whole number."
                );
            }

            inputData[field] = numberValue;

        } else {
            inputData[field] = value;
        }
    }

    return inputData;
}


// ======================================
// DISPLAY PREDICTION RESULT
// ======================================

function displayPrediction(data) {
    const resultContainer = document.getElementById("result");

    if (!resultContainer) return;

    resultContainer.style.display = "block";
    resultContainer.replaceChildren();

    const heading = document.createElement("h3");
    heading.textContent = "Marine Ecosystem Prediction";

    const prediction = document.createElement("p");
    prediction.textContent =
        "Prediction: " + data.prediction;

    const confidenceHeading = document.createElement("h4");
    confidenceHeading.textContent = "Model Confidence";

    resultContainer.append(
        heading,
        prediction,
        confidenceHeading
    );

    if (data.confidence) {
        Object.entries(data.confidence).forEach(([label, value]) => {
            const item = document.createElement("p");
            item.textContent = `${label}: ${value}%`;
            resultContainer.appendChild(item);
        });
    }
}


// ======================================
// CONNECT PREDICTION FORM TO FASTAPI
// ======================================

const predictionForm = document.getElementById("predictionForm");

if (predictionForm) {
    predictionForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const submitButton =
            document.getElementById("predictButton");

        const resultContainer =
            document.getElementById("result");

        try {
            const inputData = getMarineInput(predictionForm);

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = "Analyzing Ecosystem...";
            }

            if (resultContainer) {
                resultContainer.style.display = "block";
                resultContainer.textContent =
                    "Generating prediction...";
            }

            const result = await apiRequest(
                "/api/predict",
                inputData
            );

            if (!result.success) {
                throw new Error(
                    "Prediction could not be generated."
                );
            }

            displayPrediction(result);

        } catch (error) {
            if (resultContainer) {
                resultContainer.style.display = "block";
                resultContainer.textContent = error.message;
            }

            console.error(
                "BlueWatch prediction error:",
                error
            );

        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = "Predict Ecosystem";
            }
        }
    });
}


// ======================================
// BLUEWATCH LIVE MARINE WEATHER
// ======================================

async function loadMarineWeather() {
    const locationSelect =
        document.getElementById("weatherLocation");

    const status =
        document.getElementById("weatherStatus");

    if (!locationSelect || !status) return;

    const location = locationSelect.value;

    status.textContent = "Loading weather data...";

    try {
        const response = await fetch(
            `${API_URL}/api/marine?location=${encodeURIComponent(location)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Weather API failed"
            );
        }

        const marine =
            data.current_marine_conditions || {};

        const weather =
            data.current_weather || {};

        const forecast =
            data.seven_day_marine_forecast || {};

        const waveHeight =
            document.getElementById("waveHeight");

        const seaTemperature =
            document.getElementById("seaTemperature");

        const windSpeed =
            document.getElementById("windSpeed");

        const waveDirection =
            document.getElementById("waveDirection");

        if (waveHeight) {
            waveHeight.textContent =
                marine.wave_height != null
                    ? marine.wave_height + " m"
                    : "Unavailable";
        }

        if (seaTemperature) {
            seaTemperature.textContent =
                marine.sea_surface_temperature != null
                    ? marine.sea_surface_temperature + " °C"
                    : "Unavailable";
        }

        if (windSpeed) {
            windSpeed.textContent =
                weather.wind_speed_10m != null
                    ? weather.wind_speed_10m + " km/h"
                    : "Unavailable";
        }

        if (waveDirection) {
            waveDirection.textContent =
                marine.wave_direction != null
                    ? marine.wave_direction + "°"
                    : "Unavailable";
        }

        // Seven-day marine forecast

        const forecastContainer =
            document.getElementById("marineForecast");

        if (forecastContainer) {
            forecastContainer.replaceChildren();

            const dates = forecast.time || [];
            const waveHeights =
                forecast.wave_height_max || [];

            const waveDirections =
                forecast.wave_direction_dominant || [];

            const wavePeriods =
                forecast.wave_period_max || [];

            if (dates.length === 0) {
                forecastContainer.textContent =
                    "Seven-day forecast is currently unavailable.";

            } else {
                dates.forEach((date, index) => {
                    const day = document.createElement("div");
                    day.className = "forecast-day";

                    const heading =
                        document.createElement("strong");

                    heading.textContent = date;

                    const height =
                        document.createElement("p");

                    height.textContent =
                        "Wave: " +
                        (waveHeights[index] != null
                            ? waveHeights[index] + " m"
                            : "N/A");

                    const direction =
                        document.createElement("p");

                    direction.textContent =
                        "Direction: " +
                        (waveDirections[index] != null
                            ? waveDirections[index] + "°"
                            : "N/A");

                    const period =
                        document.createElement("p");

                    period.textContent =
                        "Period: " +
                        (wavePeriods[index] != null
                            ? wavePeriods[index] + " s"
                            : "N/A");

                    day.append(
                        heading,
                        height,
                        direction,
                        period
                    );

                    forecastContainer.appendChild(day);
                });
            }
        }

        status.textContent =
            "Weather updated successfully for " + location;

    } catch (error) {
        status.textContent =
            "Unable to load weather: " + error.message;

        console.error(
            "BlueWatch weather error:",
            error
        );
    }
}


// ======================================
// WEATHER EVENT LISTENERS
// ======================================

document.addEventListener("DOMContentLoaded", function() {
    const locationSelect =
        document.getElementById("weatherLocation");

    const refreshButton =
        document.getElementById("refreshWeather");

    if (!locationSelect || !refreshButton) return;

    locationSelect.addEventListener(
        "change",
        loadMarineWeather
    );

    refreshButton.addEventListener(
        "click",
        loadMarineWeather
    );

    loadMarineWeather();
});
