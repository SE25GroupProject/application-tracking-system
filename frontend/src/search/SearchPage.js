import React, { Component } from "react";
import $ from "jquery";
import JobTable from "./JobTable";


export default class SearchPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      searchKeywords: "",
      searchCompany: "",
      searchLocation: "",
      rows: [],
      loading: false,
    };
  }

  componentDidMount() {
    const lastSearchResults = localStorage.getItem('lastSearchResults');
    if (lastSearchResults) {
      const lastSearchFilters = JSON.parse(localStorage.getItem('lastSearchFilters'));
      this.setState({
        rows: JSON.parse(lastSearchResults),
        searchKeywords: lastSearchFilters.keywords,
        searchCompany: lastSearchFilters.company,
        searchLocation: lastSearchFilters.location
      });
		}
  }

  search() {
    if (!this.state.searchKeywords && !this.state.searchCompany && !this.state.searchLocation) {
      window.alert("Search queries cannot be empty!");
      return;
    }
    this.setState({ loading: true });
    $.ajax({
      url: "http://localhost:5000/search",
      method: "get",
      data: {
        keywords: this.state.searchKeywords,
        company: this.state.searchCompany,
        location: this.state.searchLocation,
      },
      contentType: "application/json",
      success: (data) => {
        const res = data.map((d, i) => {
          return {
            id: i,
            title: d.title,
            company: d.company,
            location: d.location,
            type: d.type,
            link: d.link,
          };
        });
        this.setState({
          loading: false,
          rows: res,
        });
        localStorage.setItem('lastSearchResults', JSON.stringify(res));
        localStorage.setItem('lastSearchFilters', JSON.stringify({
          keywords: this.state.searchKeywords,
          company: this.state.searchCompany,
          location: this.state.searchLocation
        }));
      },
      error: () => {
        window.alert("Error while fetching jobs. Please try again later");
        this.setState({
          loading: false,
        });
      },
    });
  }

  handleChange(event) {
    this.setState({ [event.target.id]: event.target.value });
  }

  render() {
    return (
      <div>
        <div className="d-flex justify-content-center my-5 ml-48 container">
          <input
            type="text"
            id="searchKeywords"
            className="form-control px-4 py-3"
            placeholder="Keywords"
            aria-label="Keywords"
            value={this.state.searchKeywords}
            onChange={this.handleChange.bind(this)}
            style={{ fontSize: 18, marginRight: 20, border: '1px solid grey' }}
          />
          <input
            type="text"
            id="searchCompany"
            className="form-control px-4 py-3"
            placeholder="Company"
            aria-label="Company"
            value={this.state.searchCompany}
            onChange={this.handleChange.bind(this)}
            style={{ fontSize: 18, marginRight: 20, border: '1px solid grey' }}
          />
          <input
            type="text"
            id="searchLocation"
            className="form-control px-4 py-3"
            placeholder="Location"
            aria-label="Location"
            value={this.state.searchLocation}
            onChange={this.handleChange.bind(this)}
            style={{ fontSize: 18, marginRight: 20, border: '1px solid grey' }}
          />
          <button
            type="button"
            className="px-4 py-3 custom-btn"
            onClick={this.search.bind(this)}
            disabled={this.state.searching}
          >
            Search
          </button>
        </div>
        <JobTable rows={this.state.rows} loading={this.state.loading} emptyMessage="Try different search parameters." />
      </div>
    );
  }
}
