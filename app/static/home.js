
        var apiKey = 'AIzaSyA79sKZO66raMNC85mJlxR9K1ge0Gg40Uo';
        // var videoId = 'Nnop2walGmM';
        var thumbnailUrl = `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;
        var elements = document.getElementsByClassName('y-vid');
        
        // Assuming there's only one element with class 'c1'
        if (elements.length > 0) {
                for(var i = 0; i < elements.length; i++){
            var element = elements[i];
            element.style.backgroundImage = `url('${thumbnailUrl}')`; // Set the background image
            element.style.backgroundRepeat = "no-repeat"; // The background image will not repeat (default is repeat)
            element.style.backgroundPosition = "center";  // The background image will be centered
        }
}
        var links = document.getElementsByClassName('y-link');
        // for(var i = 0; i < links.length; i++){
        //         var link = links[i];
        //         link.href = `/chat?q=${videoId}`;
        // }
        // Fetch the thumbnail URL for the video
        // fetch(requestUrl)
        //     .then(response => response.json())
        //     .then(data => {
        //         console.log(data);
        //         // Extract the thumbnail URL from the response
        //         var thumbnailUrl = data.items[0].snippet.thumbnails.default.url;
        //         // Set the thumbnail image source
        //         document.getElementById('thumbnail').src = thumbnailUrl;
        //     })
        //     .catch(error => console.error('Error fetching thumbnail:', error));
        function search() {
                var searchText = document.getElementById('searchInput').value;
                if (searchText.trim() !== "") {
                    var encodedText = encodeURIComponent(searchText);
                    window.location.href = `/?q=${encodedText}`;
                } else {
                    alert("Please enter a search query.");
                }
            }