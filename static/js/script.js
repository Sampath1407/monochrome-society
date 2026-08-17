// ======================================================
// MONOCHROME SOCIETY
// ======================================================


// ======================================================
// CURRENT ARTWORK
// ======================================================

const selectedArtwork =
    document.body.dataset.artwork || "wide";


// ======================================================
// MONO BUTTON
// ======================================================

const monoButton =
    document.getElementById("monoButton");

const monoCount =
    document.getElementById("monoCount");


if (monoButton && monoCount) {

    const monoKey =
        "mono_" + selectedArtwork;


    let alreadyMonod =
        localStorage.getItem(monoKey) === "true";


    let count =
        parseInt(monoCount.textContent);


    if (alreadyMonod) {
        count++;
    }


    function updateMonoButton() {

        monoButton.innerHTML = `

            ${alreadyMonod ? "♥" : "♡"}

            <span id="monoCount">
                ${count}
            </span>

            ${alreadyMonod ? "MONOED" : "MONOS"}

        `;
    }


    updateMonoButton();


    monoButton.addEventListener(
        "click",
        function () {

            if (alreadyMonod) {
                return;
            }


            count++;

            alreadyMonod = true;


            localStorage.setItem(
                monoKey,
                "true"
            );


            updateMonoButton();

        }
    );

}


// ======================================================
// CREATE STORY ELEMENT
// ======================================================

function createStoryElement(story) {

    const article =
        document.createElement("article");


    article.className =
        "story";


    const text =
        document.createElement("p");


    text.className =
        "story-text";


    text.textContent =
        `"${story.text}"`;


    const meta =
        document.createElement("div");


    meta.className =
        "story-meta";


    const user =
        document.createElement("span");


    user.textContent =
        story.user;


    const monos =
        document.createElement("span");


    monos.textContent =
        `${story.monos} MONOS`;


    meta.appendChild(user);

    meta.appendChild(monos);


    article.appendChild(text);

    article.appendChild(meta);


    return article;
}


// ======================================================
// STORY SUBMISSION
// ======================================================

const storyButton =
    document.getElementById("storyButton");

const storyInput =
    document.getElementById("storyInput");

const storyList =
    document.getElementById("storyList");


if (
    storyButton &&
    storyInput &&
    storyList
) {

    storyButton.addEventListener(
        "click",
        async function () {

            const storyText =
                storyInput.value.trim();


            if (!storyText) {

                alert(
                    "Write your story first."
                );

                return;
            }


            storyButton.disabled =
                true;


            storyButton.textContent =
                "SHARING...";


            try {

                const response =
                    await fetch(
                        `/api/stories/${selectedArtwork}`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({
                                    text: storyText
                                })
                        }
                    );


                const result =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        result.error ||
                        "Could not save story."
                    );

                }


                // Add the new story
                // without refreshing

                storyList.appendChild(
                    createStoryElement(result)
                );


                // Clear textarea

                storyInput.value = "";


            } catch (error) {

                console.error(
                    "Story submission error:",
                    error
                );


                alert(
                    "Could not save your story."
                );

            } finally {

                storyButton.disabled =
                    false;


                storyButton.textContent =
                    "SHARE STORY →";

            }

        }
    );

}


// ======================================================
// ARTIST NOTE
// ======================================================

const revealButton =
    document.getElementById(
        "revealButton"
    );

const artistNoteText =
    document.getElementById(
        "artistNoteText"
    );


if (
    revealButton &&
    artistNoteText
) {

    revealButton.addEventListener(
        "click",
        function () {

            artistNoteText.classList.toggle(
                "hidden"
            );


            if (
                artistNoteText.classList.contains(
                    "hidden"
                )
            ) {

                revealButton.textContent =
                    "REVEAL";

            } else {

                revealButton.textContent =
                    "HIDE NOTE";

            }

        }
    );

}


// ======================================================
// EXPLORE FILTERS
// ======================================================

const filterButtons =
    document.querySelectorAll(".filter");

const exploreCards =
    document.querySelectorAll(".explore-card");


if (
    filterButtons.length > 0 &&
    exploreCards.length > 0
) {

    filterButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    filterButtons.forEach(
                        function (btn) {

                            btn.classList.remove(
                                "active"
                            );

                        }
                    );


                    button.classList.add(
                        "active"
                    );


                    const selectedCategory =
                        button.textContent
                            .trim()
                            .toLowerCase();


                    exploreCards.forEach(
                        function (card) {

                            const category =
                                card.dataset.category;


                            if (
                                selectedCategory ===
                                "all"
                            ) {

                                card.style.display =
                                    "";

                            }

                            else if (
                                category ===
                                selectedCategory
                            ) {

                                card.style.display =
                                    "";

                            }

                            else {

                                card.style.display =
                                    "none";

                            }

                        }
                    );

                }
            );

        }
    );

}


// ======================================================
// SUBMIT IMAGE PREVIEW
// ======================================================

const artUpload =
    document.getElementById(
        "artUpload"
    );

const imagePreview =
    document.getElementById(
        "imagePreview"
    );


if (
    artUpload &&
    imagePreview
) {

    artUpload.addEventListener(
        "change",
        function () {

            const file =
                artUpload.files[0];


            if (!file) {
                return;
            }


            const reader =
                new FileReader();


            reader.onload =
                function (event) {

                    imagePreview.innerHTML = `

                        <img
                            src="${event.target.result}"
                            alt="Artwork preview"
                        >

                    `;

                };


            reader.readAsDataURL(file);

        }
    );

}
// ======================================================
// ARTWORK SUBMISSION
// ======================================================

const submitForm =
    document.getElementById("submitForm");


if (submitForm) {

    submitForm.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();


            const formData =
                new FormData(submitForm);


            const submitButton =
                submitForm.querySelector(
                    'button[type="submit"]'
                );


            if (submitButton) {

                submitButton.disabled =
                    true;

                submitButton.textContent =
                    "SUBMITTING...";

            }


            try {

                const response =
                    await fetch(
                        "/api/submit",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                const result =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        result.error ||
                        "Submission failed."
                    );

                }


                alert(
                    "Artwork submitted successfully! 🖤"
                );


                submitForm.reset();


                const imagePreview =
                    document.getElementById(
                        "imagePreview"
                    );


                if (imagePreview) {

                    imagePreview.innerHTML = `
                        <span>
                            IMAGE PREVIEW
                        </span>
                    `;

                }


            } catch (error) {

                console.error(
                    "Artwork submission error:",
                    error
                );


                alert(
                    error.message ||
                    "Something went wrong."
                );


            } finally {

                if (submitButton) {

                    submitButton.disabled =
                        false;

                    submitButton.textContent =
                        "SUBMIT ARTWORK →";

                }

            }

        }
    );

}
