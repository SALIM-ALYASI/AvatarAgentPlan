document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('avatarForm');
    const imageBox = document.getElementById('imageBox');
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');

    const audioBox = document.getElementById('audioBox');
    const audioInput = document.getElementById('audioInput');
    const audioName = document.getElementById('audioName');

    const generateBtn = document.getElementById('generateBtn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');

    const loadingState = document.getElementById('loadingState');
    const resultBox = document.getElementById('resultBox');
    const resultVideo = document.getElementById('resultVideo');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorBox = document.getElementById('errorBox');
    const errorMessage = document.getElementById('errorMessage');
    const statusText = document.getElementById('statusText');

    // --- Drag and Drop Logic --- //

    // Handle Image
    setupDragAndDrop(imageBox, imageInput, (file) => {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imageBox.classList.add('has-file');
            };
            reader.readAsDataURL(file);
        } else {
            alert('الرجاء اختيار صورة صالحة (JPG/PNG)');
            imageInput.value = '';
        }
    });

    imageBox.addEventListener('click', () => imageInput.click());

    // Handle Audio
    setupDragAndDrop(audioBox, audioInput, (file) => {
        if (file && (file.type.startsWith('audio/') || file.name.endsWith('.wav'))) {
            audioName.textContent = file.name;
            audioBox.classList.add('has-file');
        } else {
            alert('الرجاء اختيار ملف صوتي صالح (.wav)');
            audioInput.value = '';
        }
    });

    audioBox.addEventListener('click', () => audioInput.click());

    function setupDragAndDrop(box, input, callback) {
        box.addEventListener('dragover', (e) => {
            e.preventDefault();
            box.classList.add('drag-over');
        });

        box.addEventListener('dragleave', () => {
            box.classList.remove('drag-over');
        });

        box.addEventListener('drop', (e) => {
            e.preventDefault();
            box.classList.remove('drag-over');

            if (e.dataTransfer.files.length) {
                const file = e.dataTransfer.files[0];

                // Assign file to input manually using DataTransfer
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                input.files = dataTransfer.files;

                callback(file);
            }
        });

        input.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                callback(this.files[0]);
            }
        });
    }

    // --- Form Submission Logic --- //

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const imageFile = imageInput.files[0];
        const audioFile = audioInput.files[0];
        const quality = document.querySelector('input[name="quality"]:checked').value;

        if (!imageFile || !audioFile) {
            alert('الرجاء رفع كل من الصورة وملف الصوت.');
            return;
        }

        // Setup UI for Loading
        form.classList.add('hidden');
        errorBox.classList.add('hidden');
        loadingState.classList.remove('hidden');
        if (statusText) statusText.textContent = "جاري تحضير الملفات...";

        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('audio', audioFile);
        formData.append('quality', quality);

        // Generate a random ID for this session to track status (FastAPI assigns timestamp)
        // Since we don't know the exact timestamp FastAPI creates, we'll let FastAPI return it
        // Or we pass it. For simplicity, we'll just poll the latest or change logic if needed.
        // Actually, let's just make the status endpoint return the LATEST status globally for a single user scenario.

        let pollInterval = setInterval(async () => {
            // For a single user app, we can just poll a general "latest" status or fix the backend to use a session ID
            try {
                const res = await fetch('/status/latest');
                if (res.ok) {
                    const data = await res.json();
                    if (statusText) statusText.textContent = data.status;
                }
            } catch (e) { }
        }, 1500);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            clearInterval(pollInterval);

            if (data.status === 'success') {
                // Show Result
                loadingState.classList.add('hidden');
                resultBox.classList.remove('hidden');

                // Add cache buster to force reload
                const videoUrl = data.video_url + '?t=' + new Date().getTime();
                resultVideo.src = videoUrl;
                downloadBtn.href = data.video_url; // Download URL doesn't necessarily need cache bust

                resultVideo.play();
            } else {
                throw new Error(data.message + (data.details ? "\n" + data.details : ""));
            }

        } catch (error) {
            console.error('Error:', error);
            clearInterval(pollInterval);
            // Restore UI and show error
            loadingState.classList.add('hidden');
            form.classList.remove('hidden');
            errorBox.classList.remove('hidden');
            errorMessage.textContent = error.message;
        }
    });
});
