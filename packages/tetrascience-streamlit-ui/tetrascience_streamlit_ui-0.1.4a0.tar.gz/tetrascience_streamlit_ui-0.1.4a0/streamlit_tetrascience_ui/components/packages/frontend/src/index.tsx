import React from "react"
// import ReactDOM from "react-dom"
import ReactDOM from "react-dom/client";
import MyComponent from "./MyComponent"
import AtomsShowcase from "./AtomsShowcase/AtomsShowcase"
import MoleculesShowcase from "./MoleculesShowcase/MoleculesShowcase"
import OrganismsShowcase from "./OrganismsShowcase/OrganismsShowcase"
import HistogramComponent from "./HistogramComponent/HistogramComponent"

import { StApp } from "./App"

ReactDOM.createRoot(document.getElementById("root")!).render(<StApp />);