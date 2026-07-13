function unlockPost(event, btn) {
    event.stopPropagation();
    const post = btn.closest('.post');
    const postId = post.dataset.id;
    const passInput = post.querySelector('.unlock-password');
    const passwordValue = passInput ? passInput.value : '';
    if (!passwordValue.trim()) {
        alert("Please enter the password");
        return;
    }
    const formData = new FormData();
    formData.append('password', passwordValue);
    fetch(`/unlock/${postId}`, {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (response.status === 401) {
                alert("Incorrect password");
                return null;
            }
            if (!response.ok) {
                throw new Error("Server error: " + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            const img = post.querySelector('.post-img');
            img.src = data.img;
            img.style.display = 'block';
            post.querySelector('.bird-loc').innerText = data.loc;
            post.querySelector('.password-lock-form').style.display = 'none';

            const likeBtn = post.querySelector('.like-button');
            if (likeBtn) {
                likeBtn.classList.remove('locked');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Server error: check the Flask terminal! Details: " + error.message);
        });
}

function toggleLike(event, btn) {
    event.stopPropagation();
    if (btn.classList.contains('locked')) {
        return;
    }
    const post = btn.closest('.post');
    const postId = post.dataset.id;
    if (!postId || postId === "0") return;
    fetch(`/like/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.status === 401) {
                alert("Please login to like posts.");
                return null;
            }
            if (response.status === 403) {
                alert("This post is locked.");
                return null;
            }
            if (!response.ok) {
                throw new Error("HTTP Status " + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            post.querySelector('.like-count').innerText = data.likes_count;
            const heart = post.querySelector('.heart-icon');
            heart.classList.toggle('liked', data.action === 'liked');
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Server error: check the Flask terminal! Details: " + error.message);
        });
}

function toggleModal(show) {
    const modal = document.getElementById('upload-modal');
    if (show) modal.classList.add('active');
    else modal.classList.remove('active');
}

const photoInput = document.getElementById('photo-upload');
if (photoInput) {
    photoInput.addEventListener('change', function (e) {
        const fileName = e.target.files[0] ? e.target.files[0].name : 'Select an image...';
        document.getElementById('file-name-display').textContent = fileName;
    });
}

const scrollHint = document.getElementById('scroll-hint');
if (scrollHint) {
    if (localStorage.getItem('birdwatcher_scroll_hint_seen')) {
        scrollHint.classList.add('hidden');
    } else {
        let hintDismissed = false;
        const dismissHint = function () {
            if (hintDismissed) return;
            hintDismissed = true;
            scrollHint.classList.add('hidden');
            localStorage.setItem('birdwatcher_scroll_hint_seen', 'true');
            document.body.removeEventListener('scroll', dismissHint);
        };
        document.body.addEventListener('scroll', dismissHint, { passive: true });
    }
}