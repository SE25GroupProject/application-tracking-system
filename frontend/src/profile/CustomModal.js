import React, { useState } from "react";
import Select from "react-select";
import { Modal, ModalBody, ModalDialog, ModalFooter } from "react-bootstrap";
import ModalHeader from "react-bootstrap/ModalHeader";
import axios from "axios";
import { toDropdownOptionsList } from "../data/Constants";

const CustomModal = (props) => {
  const { options, name, profile, setProfile, setModalOpen, updateProfile } =
    props;
  const [data, setData] = useState(profile[name]);

  const handleSave = () => {
    updateProfile({ [name]: data });

    setModalOpen(false);
  };

  return (
    <Modal show={true} centered size="lg">
      <ModalHeader style={{ backgroundColor: "#296E85", color: "#fff" }}>
        <h5 class="modal-title">Set preferences</h5>
        <button
          type="button"
          class="btn-close"
          aria-label="Close"
          onClick={() => setModalOpen(false)}
          style={{ backgroundColor: "#fff" }}
        ></button>
      </ModalHeader>
      <ModalBody>
        <Select
          defaultValue={toDropdownOptionsList(profile[name])}
          isSearchable
          isClearable
          tabSelectsValue
          isMulti
          options={options}
          onChange={(ele) => {
            setData(Array.from(ele, (item) => item.label));
            console.log(data);
          }}
        />
      </ModalBody>
      <ModalFooter>
        <button
          type="button"
          className="custom-btn px-3 py-2"
          onClick={handleSave}
        >
          Save
        </button>
      </ModalFooter>
    </Modal>
  );
};

export default CustomModal;
