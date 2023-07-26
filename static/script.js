const customButton = document.getElementById('custom-button');
const customPopup = document.getElementById('custom-popup');
const customUrlInput = document.getElementById('custom-url-input');
const customRedirect = document.getElementById('custom-redirect-input');
const customAuthenticationInput = document.getElementById('authentication-input');
const cancelButton = document.getElementById('cancel-button');
const saveButton = document.getElementById('save-button');
const container = document.querySelector('.container');
const shortenForm = document.getElementById('shorten-form');
const shortenInput = document.getElementById('shorten-input');
const shortenButton = document.getElementById('shorten-button');
const shortenResult = document.getElementById('shorten-result');
const shortenedUrl = document.getElementById('shortened-url');


shortenForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const url = shortenInput.value.trim();

    if (url !== '') {
        const data = new URLSearchParams();
        data.append('url', url);

        fetch('/api/add_shortened', {
            method: 'POST',
            body: data,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            const shortened = "https://moekyun.me/"+data; 
            shortenedUrl.href = shortened;
            shortenedUrl.textContent = shortened;
            shortenResult.style.display = 'block';
            container.classList.add('show-result');
        })
        .catch(error => {
            console.error('Error:', error);
        });
        shortenInput.value = '';
    }
});

customButton.addEventListener('click', () => {
    customPopup.style.display = 'block';
});

cancelButton.addEventListener('click', () => {
    customPopup.style.display = 'none';
});


saveButton.addEventListener('click', () => {
    const customUrl = customUrlInput.value;
    const authentication = customAuthenticationInput.value;
    const redirect = customRedirect.value;

    console.log(customUrl);
    console.log(authentication);
    console.log(redirect);
    const data = new URLSearchParams();
    data.append('url', redirect);
    data.append('custom', customUrl);
    
    fetch('/api/add_custom', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-AUTHENTICATION': authentication 
      },
      body: data
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      const shortened = "https://moekyun.me/"+data; 
      shortenedUrl.href = shortened;
      shortenedUrl.textContent = shortened;
      shortenResult.style.display = 'block';
      container.classList.add('show-result');
    })
    .catch(error => {
      shortenedUrl.href = "https://i.pinimg.com/1200x/df/2d/a3/df2da37278e0270d873015fb5613e57a.jpg";
      shortenedUrl.textContent = "You do not have the power of god and anime on your side! (An error occured)";
      shortenResult.style.display = 'block';
      container.classList.add('show-result');
    });

    customPopup.style.display = 'none';
  });
document.addEventListener('click', (event) => {
    const popupContent = document.querySelector('.popup-content');
    if (!popupContent.contains(event.target) && event.target !== customButton) {
        customPopup.style.display = 'none';
    }
});