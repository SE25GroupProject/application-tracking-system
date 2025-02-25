import React, { Component } from 'react'
import $ from 'jquery'
import '../static/resume.css'

export default class ManageResumePage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      fileNames: [],
      loading: false
    }
  }

  getFiles() {
    $.ajax({
      url: 'http://127.0.0.1:5000/resume',
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
        'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
        'Access-Control-Allow-Credentials': 'true'
      },
      credentials: 'include',
      success: (message, textStatus, response) => {
        console.log(message)
        this.setState({
          fileNames: message.filenames,
        })
      }
    })
  }


    previewResume(resume_idx) {
        $.ajax({
            url: 'http://127.0.0.1:5000/resume/' + resume_idx,
            method: 'GET',
            headers: {
              'Authorization': 'Bearer ' + localStorage.getItem('token'),
              'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
              'Access-Control-Allow-Credentials': 'true'
            },
            xhrFields: { responseType: 'blob' },
            credentials: 'include',
            success: (message, textStatus, response) => {
              console.log(message)
              if(message){
                window.open(URL.createObjectURL(message), '_blank');
              }
            }
          })
    }

  uploadResume = (e) => {
    e.preventDefault();

    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".pdf"; // Adjust allowed file types if needed

    fileInput.addEventListener("change", (event) => {
      if (event.target.files.length == 0) {
        return;
      }

        this.setState({loading: true});
        let formData = new FormData()
        const file = event.target.files[0];
        formData.append('file', file);
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
                console.log("Upload successful:", msg)
                this.setState({ fileNames: [...this.state.fileNames, file.name] })
            }
        }).always(() => this.setState({loading: false}))
        
    });

    fileInput.click();
  }

  componentDidMount() {
    this.getFiles()
  }

  componentWillUnmount() {
    if (this.state.previewUrl) {
      URL.revokeObjectURL(this.state.previewUrl);
    }
  }
  

  render() {
    return (
      <div className="pagelayout">
        
        <form id="upload-file" method="post" encType="multipart/form-data">
          <button
            id="upload-file-btn"
            onClick={(event) => {
                if (!this.state.loading) {
                    this.uploadResume(event)
                }
            }}
            disabled={this.state.loading}
            type="button"
            style={{
                display: 'block',
                margin: '0 auto'
            }}
          >
            {this.state.loading ? 'Uploading...' : 'Uploade New'}
          </button>

          <div style={{ margin: '1.5em' }}></div>
          <div>
            <h2>Uploaded Documents</h2>
            <table>
              <thead>
                <tr>
                  <th className="tablecol1">Documents</th>
                  <th className="tablecol2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {this.state.fileNames.map((fileName, index) => (
                  <tr key={index}>
                    <td className="tablecol1">{fileName}</td>
                    <td className="tablecol2">
                      <button
                        id="view-file-btn"
                        onClick={() => this.previewResume(index)}
                        type="button"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </form>
      </div>
    )
  }
}
