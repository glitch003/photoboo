photoDisplay = null;
$( document ).ready(function() {
	photoDisplay = new PhotoDisplay();

	bodyId = $("body").attr("id");
	if (bodyId == "random") {
		photoDisplay.playRandomPhotos();
	} else {
		photoDisplay.playLatestPhoto();
	}
});