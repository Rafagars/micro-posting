tinymce.init({
  selector: '#mytextarea',
  plugins: "a11ychecker casechange formatpainter linkchecker autolink lists checklist media mediaembed permanentpen powerpaste table advtable tinymcespellchecker emoticons image imagetools",
  toolbar: "a11ycheck casechange checklist formatpainter permanentpen table emoticons image media",
  toolbar_mode: 'floating',
  file_picker_types: 'image media',
  images_upload_url: '/imageuploader',
  automatic_uploads: false,
  images_upload_base_path: '/static/media',
  width: "100%",
});