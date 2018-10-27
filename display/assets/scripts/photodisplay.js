function PhotoDisplay() {
	this.apiUrl = 'https://20mission.org/photoboo/api/photos/';
	this.lastPhotoCtime = 0;
	this.timeBetweenPhotos_s = 5;
}

PhotoDisplay.prototype.getRandomPhoto = function() {
	self = this;
	url = this.apiUrl + "random";
	$.ajax({
		dataType: "json",
		url: url,
		success: function(request) {
			self.hideError();
			self.displayPhoto(request);
			console.log(request);
		},
		error: function(error) {
			self.displayError("Could not contact API server");
			console.log(error);
		}
	});
}

PhotoDisplay.prototype.playRandomPhotos = function() {
	self = this;
	self.getRandomPhoto();
	setInterval(function() {
		self.getRandomPhoto();
	}, this.timeBetweenPhotos_s * 1000);
}

PhotoDisplay.prototype.playLatestPhoto = function() {
	self = this;
	this.getLatestPhoto();
	setInterval(function() {
		self.getLatestPhoto();
	}, this.timeBetweenPhotos_s * 200);
}

PhotoDisplay.prototype.getPhotoById = function(id) {
	self = this;
	url = this.apiUrl + id;
	$.ajax({
		dataType: "json",
		url: url,
		success: function(request) {
			self.hideError();
			self.displayPhoto(request);
			console.log(request);
		},
		error: function(error) {
			self.displayError("Could not contact API server");
			console.log(error);
		}
	});
}

PhotoDisplay.prototype.listPhotos = function() {
	self = this;
	url = this.apiUrl;
	$.ajax({
		dataType: "json",
		url: url,
		success: function(request) {
			self.hideError();
			console.log(request);
		},
		error: function(error) {
			self.displayError("Could not contact API server");
			console.log(error);
		}
	});
}

PhotoDisplay.prototype.getLatestPhoto = function() {
	self = this;
	url = this.apiUrl;
	lastPhotoCtime = this.lastPhotoCtime;
	$.ajax({
		dataType: "json",
		url: url,
		success: function(request) {
			self.hideError();
			localMaxCtime = 0;
			localMaxCtimeId = 0;
			for (var i = 0; i < request.length; i++) {
				photo = request[i];
				if (photo.ctime > localMaxCtime) {
					self.lastPhotoCtime = photo.ctime
					self.getPhotoById(photo.id);
					break;
				}
				console.log(photo);
			}
		},
		error: function(error) {
			self.displayError("Could not contact API server");
			console.log(error);
		}
	});
}

PhotoDisplay.prototype.displayPhoto = function(photo) {
	console.log("Displaying photo:");
	loadingPhoto = $("#loading_photo");
	loadedPhoto = $("#loaded_photo");
	loadingPhoto.css({ opacity: 0.0 });
	url = "https://20mission.org" + photo.url;
	background = 'url(' + url + ')';
	loadingPhoto.css(
		"background-image",
		background
	);
	loadingPhoto.fadeTo("slow", 1.0, function() {
		loadedPhoto.css(
			"background-image",
			background
		);
		loadingPhoto.css({opacity: 0.0});
  	});
  	/* */
  	/*
	$("#photo").attr(
		"src",
		"data:image/jpg;base64," + photo.data
	);
	/* */
	/*
	url = "https://20mission.org" + photo.url;
	$("#photo").css("background-image", "url('" + url + "')");
	/* */

}

PhotoDisplay.prototype.displayError = function(message) {
	console.log("ERROR: " + message);
	$("#message_bar").html(message);
	$("#message_bar").slideDown();
}

PhotoDisplay.prototype.hideError = function() {
	$("#message_bar").slideUp();
}