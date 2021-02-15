import React, { useState } from "react";
import Button from "./Button";
import SelectTable from "./SelectTable";
import FormController from "../components/forms/FormController";
import { api } from "../services/api.js";

const ActionWindow = ({ setData }) => {
  const [from_table, setFromTable] = useState("/exemplary-object");
  const [to_table, setToTable] = useState("/exemplary-object");
  const [body, setBody] = useState([]);

  function handleRequest() {
    api
      .get(from_table, {
        headers: {
          Authorization:
            "Bearer " + JSON.parse(sessionStorage.getItem("token")).token,
        },
      })
      .then((res) => {
        if (res.data.length === 0) {
          window.alert(
            "The table you wanted to fetch is either empty, or you don't have access to any of its rows"
          );
        }
        setData(res.data);
      });
  }

  function handleAddition() {
    window.alert(to_table);
    api
      .post(to_table, JSON.parse(body), {
        headers: {
          Authorization:
            "Bearer " + JSON.parse(sessionStorage.getItem("token")).token,
        },
      })
      .then((res) => window.alert(res));
  }

  return (
    <div className="auth-inner">
      {body}
      <SelectTable setTable={setFromTable} />
      <Button label="Get available rows" onClick={handleRequest} />
      <SelectTable setTable={setToTable} />
      <FormController
        to_table={to_table}
        setBody={setBody}
        handleAddition={handleAddition}
      />
    </div>
  );
};

export default ActionWindow;
