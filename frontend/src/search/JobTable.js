import React, { Component } from "react";
import $ from "jquery";
import { Spinner } from "react-bootstrap";

const columns = [
  {
    label: "Company",
    id: "company",
  },
  {
    label: "Job Title",
    id: "title",
  },
  {
    label: "Location",
    id: "location",
  },
  {
    label: "Type",
    id: "type",
  },
  {
    label: "Actions",
    id: "link",
  },
];

export default class JobTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      /** Map of external IDs to internal IDs of saved jobs */
      savedApps: {},
    };
  }

  componentDidMount() {
    // Fetch list of saved application ids
    $.ajax({
      url: "http://127.0.0.1:5000/applications",
      method: "GET",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      success: (data) => {
        const savedApps = {};
        data.forEach(d => {
          savedApps[d.externalId] = d.id;
        });
        this.setState({ savedApps });
      },
      error: () => {
        window.alert("Error while fetching saved applications. Please try again later");
      },
    });
  }

  saveJob(job) {
    $.ajax({
      url: "http://127.0.0.1:5000/applications",
      method: "POST",
      data: JSON.stringify({
        application: job,
      }),
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      contentType: "application/json",
      success: (data) => {
        this.setState({
          savedApps: { ...this.state.savedApps, [job.externalId]: data.id },
        });
      },
    });
  }

  unsaveJob(job) {
    const internalId = this.state.savedApps[job.externalId];
    $.ajax({
      url: "http://127.0.0.1:5000/applications/" + internalId,
      method: "DELETE",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      success: (data) => {
        const { [job.externalId]: _, ...remainingApps } = this.state.savedApps;
        this.setState({
          savedApps: remainingApps,
        });
      },
    });
  }

  render() {
    const rows = this.props.rows;

    return (
      <div>
        {!this.props.loading ? (<>
          <table
            className="table my-4"
            style={{
              boxShadow: "0px 5px 12px 0px rgba(0,0,0,0.1)",
            }}
          >
            <thead>
              <tr>
                {columns.map((column) => {
                  return (
                    <th
                      className="p-3"
                      key={column.id + "_th"}
                      style={{
                        fontSize: 18,
                        fontWeight: "500",
                        backgroundColor: "#2a6e85",
                        color: "#fff",
                      }}
                    >
                      {column.label}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                return (
                  <tr key={row.id}>
                    {columns.map((column) => {
                      const value = row[column.id];
                      if (column.id !== "link") {
                        return (
                          <td className="p-2" key={column.id}>
                            {value}
                          </td>
                        );
                      }
                      const addButton = this.state.savedApps.hasOwnProperty(
                        row.externalId
                      ) ? (
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={this.unsaveJob.bind(this, row)}
                        >
                          Saved
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="btn add-btn"
                          onClick={this.saveJob.bind(this, row)}
                        >
                          Save
                        </button>
                      )
                      return (
                        <td key={row.id + "_func"} className="p-3">
                          <div className="d-flex gap-2">
                            <a
                              type="button"
                              className="add-btn px-3 py-2 text-decoration-none"
                              href={value}
                              target="_blank"
                            >
                              Apply
                            </a>
                            {addButton}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
          {this.props.rows.length === 0 &&
            <div className="text-center">No jobs found. {this.props.emptyMessage}</div>
          }
        </>) : (
          // Loading spinner
          <div className="d-flex justify-content-center my-5">
            <Spinner animation="border" style={{ fontSize: 15 }} />
          </div>
        )}
      </div>
    );
  }
}
