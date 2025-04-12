import React, { useState, useEffect } from "react";
import JobTable from "../search/JobTable";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSyncAlt } from "@fortawesome/free-solid-svg-icons";

const Recommendations = (props) => {
  const [recommendedJobs, setRecommendedJobs] = useState([]);
  const [isFetchingJobs, setIsFetchingJobs] = useState(true);

  useEffect(() => {
    const lastMatchResults = localStorage.getItem("lastMatchResults");
    const lastMatchTime = localStorage.getItem("lastMatchTime");
    if (
      lastMatchResults &&
      new Date().getTime() - lastMatchTime < 1000 * 60 * 60
    ) {
      setRecommendedJobs(JSON.parse(lastMatchResults));
      setIsFetchingJobs(false);
    } else {
      fetchRecommendations();
    }
  }, []);

  useEffect(() => {
    const lastMatchTime = localStorage.getItem("lastMatchTime");
    if (lastMatchTime) {
      fetchRecommendations();
    }
  }, [props.profile]);

  const fetchRecommendations = async () => {
    try {
      setIsFetchingJobs(true);
      const response = await fetch("http://localhost:5000/getRecommendations", {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
          "Access-Control-Allow-Origin": "http://localhost:3000",
          "Access-Control-Allow-Credentials": "true",
        },
        method: "GET",
      });
      const data = await response.json();
      if (data && data["error"]) {
        throw new Error(data["error"]);
      } else {
        localStorage.setItem("lastMatchTime", new Date().getTime());
        localStorage.setItem("lastMatchResults", JSON.stringify(data));
        setRecommendedJobs(data);
      }
    } catch (error) {
      console.log(error.message);
    } finally {
      setIsFetchingJobs(false);
    }
  };

  return (
    <div className="container">
      <h2 class="d-flex align-items-center justify-content-center mt-4 mb-5">
        Recommended Jobs &nbsp;
        <button className="btn btn-secondary" onClick={fetchRecommendations}>
          <FontAwesomeIcon icon={faSyncAlt} />
        </button>
      </h2>
      <JobTable
        rows={recommendedJobs}
        loading={isFetchingJobs}
        emptyMessage="Make sure you've filled out your profile."
      />
    </div>
  );
};

export default Recommendations;
