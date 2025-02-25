import React, { Component } from 'react'
import $ from 'jquery'
import '../static/resume.css'


export default class ManageResumePage extends Component {
  constructor (props) {
    super(props)
    this.state = {
      fileName: '',
      fileuploadname:'',
      previewUrl: null,
      modelResponse: '',
      modelPrompt: 'yo',
      loading: false
    }

    console.log("***");
    console.log(localStorage.getItem('token'));
    this.getFiles.bind(this);

  }

  getFiles () {
    $.ajax({
          url: 'http://127.0.0.1:5000/resume',
          method: 'GET',
          headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token'),
            'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
            'Access-Control-Allow-Credentials': 'true'
          },
          xhrFields: {
            responseType: 'blob'
            },
      credentials: 'include',
          success: (message, textStatus, response) => {
            console.log(response.getResponseHeader('x-fileName'))
            this.setState({ fileName: response.getResponseHeader('x-fileName')});
            this.setState({ resumeDownloadContent: message});
            this.setState({ previewUrl: URL.createObjectURL(message)});
          }
      })
}

    previewResume() {
        if (this.state.previewUrl) {
        window.open(this.state.previewUrl, '_blank');
        }
    }

    handleChange(event) {
    var name = event.target.files[0].name;
    console.log(`Selected file - ${event.target.files[0].name}`);
    this.setState({ fileuploadname: name});

    }

    uploadResume() {
        this.setState({ fileName: this.state.fileuploadname});
        console.log(this.value);
        const fileInput = document.getElementById('file').files[0];
        //console.log(fileInput);

        let formData = new FormData();
        formData.append('file', fileInput );
        //console.log(formData);

        $.ajax({
          url: 'http://127.0.0.1:5000/resume',
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token'),
            'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
            'Access-Control-Allow-Credentials': 'true'
          },
          data: formData,
          contentType: false,
          cache: false,
          processData: false,
          success: (msg) => {
                console.log(msg)
          }
          })
    }

 downloadResume(){
  $.ajax({
          url: 'http://127.0.0.1:5000/resume',
          method: 'GET',
          headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token'),
            'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
            'Access-Control-Allow-Credentials': 'true'
          },
          xhrFields: {
            responseType: 'blob'
        },
          success: (message, textStatus, response) => {
            console.log(message)
            console.log(textStatus)
            console.log(response)

            var a = document.createElement('a');
            var url = window.URL.createObjectURL(message);
            a.href = url;
            a.download = 'resume.pdf';
            document.body.append(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
          }
          })
 }

    promptModel = async (e) => {
        e.preventDefault()
        console.log("prompting model...")
        this.setState({loading: true})

        $.ajax({
            url: 'http://127.0.0.1:5000/prompt',
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
                'Access-Control-Allow-Credentials': 'true',
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({prompt: this.state.modelPrompt}),
            success: (response) => {
                this.setState({
                    modelResponse: response.response,
                    loading: false
                });
            },
            error: (xhr, status, error) => {
                console.error("Error fetching response: ", error);
                this.setState({
                    modelResponse: "An error occured while fetching the response",
                    loading: false
                })
            }

        })
    }

 componentDidMount () {
    // fetch the data only after this component is mounted
    this.getFiles()
  }

  componentWillUnmount() {
    if (this.state.previewUrl) {
      URL.revokeObjectURL(this.state.previewUrl);
    }
  }
  

  render() {
    return (

    <form class="pagelayout" id="upload-file" method="post" encType="multipart/form-data">
        <input id = "file" name="file" type="file" onChange={this.handleChange.bind(this)}></input>
        <button id="upload-file-btn" onClick={this.uploadResume.bind(this)} type="button">Upload</button>

        <div style={{margin: '2em'}}></div>
        <div >

        <h2>Uploaded Documents</h2>
            <table>
            <thead>
              <tr>
                <th className="tablecol1">Documents</th>
                <th className="tablecol2">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="tablecol1">{this.state.fileName}</td>
                <td className="tablecol2">
                  <button id="download" onClick={this.downloadResume.bind(this)} type="button">Download</button>
                  <button id="preview" onClick={this.previewResume.bind(this)} type="button">View</button>
                </td>
              </tr>
              </tbody>
          </table>
          <div>
            <button id="sendprompt" onClick={this.promptModel} type="button">test llm</button>
            <h3>model output:</h3>
            <p>{this.state.modelResponse}</p>
          </div>
        </div>
      </form>
    )
  }
}