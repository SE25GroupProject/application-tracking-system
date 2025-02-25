import React, { Component } from 'react'
import $ from 'jquery'
import '../static/resume.css'

export default class ManageResumePage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      fileNames: [],
      selectedFiles: null,
      resumeDownloadContent: null,
      previewUrl: null,
      modelResponse: '',
      modelPrompt: 'yo',
      loading: false
    }
  }

  getFiles() {
    $.ajax({
      url: 'http://127.0.0.1:5001/resume',
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
        'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
        'Access-Control-Allow-Credentials': 'true'
      },
      xhrFields: { responseType: 'blob' },
      credentials: 'include',
      success: (message, textStatus, response) => {
        console.log(response.getResponseHeader('x-fileName'))
        this.setState({
          fileNames: [response.getResponseHeader('x-fileName')],
          resumeDownloadContent: message
            this.setState({ previewUrl: URL.createObjectURL(message)});
        })
      }
    })
  }


    previewResume() {
        if (this.state.previewUrl) {
        window.open(this.state.previewUrl, '_blank');
        }
    }

  handleChange(event) {
    const files = event.target.files
    if (files.length > 0) {
      const fileNames = []
      for (let i = 0; i < files.length; i++) {
        fileNames.push(files[i].name)
      }
      console.log("Selected files:", fileNames)
      this.setState({ selectedFiles: files, fileNames })
    }
  }

  uploadResume() {
    const files = this.state.selectedFiles
    if (!files) {
      console.log("No files selected")
      return
    }
    let formData = new FormData()
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }
    $.ajax({
      url: 'http://127.0.0.1:5001/resume',
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
        // Optionally refresh the file list
        this.getFiles()
      }
    })
  }

  downloadResume() {
    $.ajax({
      url: 'http://127.0.0.1:5001/resume',
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
        'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
        'Access-Control-Allow-Credentials': 'true'
      },
      xhrFields: { responseType: 'blob' },
      success: (message, textStatus, response) => {
        const a = document.createElement('a')
        const url = window.URL.createObjectURL(message)
        a.href = url
        a.download = 'resume.pdf'
        document.body.append(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
      }
    })
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
        {/* No extra <h1> here, since App.js already shows "Application Tracking System" */}
        
        <form id="upload-file" method="post" encType="multipart/form-data">
          <input
            id="file"
            name="file"
            type="file"
            multiple
            onChange={this.handleChange.bind(this)}
          />
          <button
            id="upload-file-btn"
            onClick={this.uploadResume.bind(this)}
            type="button"
          >
            Upload
          </button>

          <div style={{ margin: '2em' }}></div>
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
                        id="download"
                        onClick={this.downloadResume.bind(this)}
                        type="button"
                      >
                        Download
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
