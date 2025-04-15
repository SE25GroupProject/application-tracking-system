import { Button, Col, Form, Row } from "react-bootstrap";
import React, { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import axios from "axios";
import { CONSTANTS } from "../data/Constants";

// forwardRef again here!
// Dropdown needs access to the DOM of the Menu to measure it
const FilteredDropdown = React.forwardRef(
  (
    {
      children,
      style,
      className,
      "aria-labelledby": labeledBy,
      createNewProfile,
    },
    ref
  ) => {
    const [value, setValue] = useState("");

    return (
      <div
        ref={ref}
        style={style}
        className={className}
        aria-labelledby={labeledBy}
      >
        <Row className="flex-nowrap mx-2">
          <Col xs="auto" className="my-1 px-0">
            <Form.Label htmlFor="newProfileName" hidden>
              New Profile Name
            </Form.Label>
            <Form.Control
              autoFocus
              className="w-auto"
              placeholder="Type to filter..."
              onChange={(e) => setValue(e.target.value)}
              value={value}
              id="newProfileName"
              aria-label="newProfileName"
            />
          </Col>

          <Col xs="auto">
            <Button
              disabled={
                !value ||
                React.Children.toArray(children).some(
                  (child) =>
                    child.props.children.toLowerCase() === value.toLowerCase()
                )
              }
              size="sm"
              className="my-1"
              onClick={() => {
                createNewProfile(value);
                setValue("");
              }}
              data-testid="Add Profile Button"
            >
              <FontAwesomeIcon icon={faPlus} size="sm" title="Add Profile" />
            </Button>
          </Col>
        </Row>

        <ul className="list-unstyled">
          {React.Children.toArray(children).filter(
            (child) =>
              !value ||
              child.props.children.toLowerCase().includes(value.toLowerCase())
          )}
        </ul>
      </div>
    );
  }
);

export default FilteredDropdown;
