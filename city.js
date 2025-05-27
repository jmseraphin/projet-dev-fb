const url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities";
const options = {
  method: "GET",
  headers: {
    "X-RapidAPI-Key": "49d99994c3mshc5677ea703a9c79p14c83fjsna105fb86e26d",
    "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
  }
};

fetch(url, options)
  .then(response => response.json())
  .then(data => {
    data.data.forEach(city => {
      console.log(city.name); // Affiche le nom de la ville
    });
  })
  .catch(error => console.error(error));