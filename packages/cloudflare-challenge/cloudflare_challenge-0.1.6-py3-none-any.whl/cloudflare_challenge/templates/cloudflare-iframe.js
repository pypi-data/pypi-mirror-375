function blob2File(fileInputElement, blob, filename) {

    function _blob2Files() {
        const file = new File([blob], filename, { type: "image/*", lastModified: new Date().getTime() })
        const container = new DataTransfer()
        container.items.add(file)
        return container
    }

    fileInputElement.files = _blob2Files().files
}
(function () {

    fetch(image_url).then((resp) => {
        if (resp.ok)
            return resp.blob()
    }).then((blob) => {
        const file = document.getElementById('file-input')
        blob2File(file, blob, image_name)
        const form = document.forms["challenge-upload"]
        form.submit();
    })

})()
