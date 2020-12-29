tinymce.init({
  selector: '#mytextarea',
  plugins: "autolink lists media powerpaste table emoticons image imagetools",
  toolbar: "table emoticons image media",
  toolbar_mode: 'floating',
  file_picker_types: 'image media',
  images_upload_url: '/imageuploader',
  automatic_uploads: false,
  images_upload_base_path: '/static/media',
  width: "100%",
});