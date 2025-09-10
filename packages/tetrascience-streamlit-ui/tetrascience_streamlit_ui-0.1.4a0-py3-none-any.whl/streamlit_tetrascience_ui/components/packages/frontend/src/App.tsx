import React, { useRef } from "react"
import { ComponentRouter } from "./componentRouter"

import HistogramComponent from "./HistogramComponent/HistogramComponent"
import ButtonAtoms from "./atoms/Button"
import BadgeAtoms from "./atoms/Badge"
import ButtonControlAtoms from "./atoms/ButtonControl"
import CardAtoms from "./atoms/Card"
import CheckboxAtoms from "./atoms/Checkbox"
import CodeEditorAtoms from "./atoms/CodeEditor"
import DropdownAtoms from "./atoms/Dropdown"
import ErrorAlertAtoms from "./atoms/ErrorAlert"
import IconAtoms from "./atoms/Icon"
import InputAtoms from "./atoms/Input"
import LabelAtoms from "./atoms/Label"
import MarkdownDisplayAtoms from "./atoms/MarkdownDisplay"
import MenuItemAtoms from "./atoms/MenuItem"
import ModalAtoms from "./atoms/Modal"
import PopConfirmAtoms from "./atoms/PopConfirm"
import SupportiveTextAtoms from "./atoms/SupportiveText"
import TabAtoms from "./atoms/Tab"
import TextareaAtoms from "./atoms/Textarea"
import ToastAtoms from "./atoms/Toast"
import ToggleAtoms from "./atoms/Toggle"
import TooltipAtoms from "./atoms/Tooltip"
import ProtocolYamlCardMolecules from "./molecules/ProtocolYamlCard"
import AppHeaderMolecules from "./molecules/AppHeader"
import NavbarMolecules from "./molecules/Navbar"
import SidebarMolecules from "./molecules/Sidebar"
import BarGraphOrganisms from "./organisms/BarGraph"
import ChromatogramOrganisms from "./organisms/Chromatogram"
import HeatmapOrganisms from "./organisms/Heatmap"
import HistogramOrganisms from "./organisms/Histogram"
import LineGraphOrganisms from "./organisms/LineGraph"
import PieChartOrganisms from "./organisms/PieChart"
import ScatterGraphOrganisms from "./organisms/ScatterGraph"
import FormFieldMolecules from "./molecules/FormField"
import LaunchContentMolecules from "./molecules/LaunchContent"
import ProtocolConfigurationMolecules from "./molecules/ProtocolConfiguration"
import PythonEditorModalMolecules from "./molecules/PythonEditorModal"
import SelectFieldMolecules from "./molecules/SelectField"
import TabGroupMolecules from "./molecules/TabGroup"

import {
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import MyComponent from "./MyComponent"
import { useAutoHeight } from "./hooks/useAutoHeight"

const crouter = new ComponentRouter()

crouter.declare("my_component", MyComponent)
crouter.declare("histogram_component", HistogramComponent)
crouter.declare("button", ButtonAtoms)
crouter.declare("badge", BadgeAtoms)
crouter.declare("button_control", ButtonControlAtoms)
crouter.declare("card", CardAtoms)
crouter.declare("checkbox", CheckboxAtoms)
crouter.declare("code_editor", CodeEditorAtoms)
crouter.declare("dropdown", DropdownAtoms)
crouter.declare("error_alert", ErrorAlertAtoms)
crouter.declare("icon", IconAtoms)
crouter.declare("input", InputAtoms)
crouter.declare("label", LabelAtoms)
crouter.declare("markdown_display", MarkdownDisplayAtoms)
crouter.declare("menu_item", MenuItemAtoms)
crouter.declare("modal", ModalAtoms)
crouter.declare("pop_confirm", PopConfirmAtoms)
crouter.declare("supportive_text", SupportiveTextAtoms)
crouter.declare("tab", TabAtoms)
crouter.declare("textarea", TextareaAtoms)
crouter.declare("toast", ToastAtoms)
crouter.declare("toggle", ToggleAtoms)
crouter.declare("tooltip", TooltipAtoms)
crouter.declare("protocol_yaml_card", ProtocolYamlCardMolecules)
crouter.declare("app_header", AppHeaderMolecules)
crouter.declare("navbar", NavbarMolecules)
crouter.declare("sidebar", SidebarMolecules)
crouter.declare("bar_graph", BarGraphOrganisms)
crouter.declare("chromatogram", ChromatogramOrganisms)
crouter.declare("heatmap", HeatmapOrganisms)
crouter.declare("histogram", HistogramOrganisms)
crouter.declare("line_graph", LineGraphOrganisms)
crouter.declare("pie_chart", PieChartOrganisms)
crouter.declare("scatter_graph", ScatterGraphOrganisms)
crouter.declare("form_field", FormFieldMolecules)
crouter.declare("launch_content", LaunchContentMolecules)
crouter.declare("protocol_configuration", ProtocolConfigurationMolecules)
crouter.declare("python_editor_modal", PythonEditorModalMolecules)
crouter.declare("select_field", SelectFieldMolecules)
crouter.declare("tab_group", TabGroupMolecules)

function App(
  props: ComponentProps<{ comp: string; props: any; [key: string]: any }>
) {
  const { args, disabled, theme } = props

  const container = useRef(null)
  const safeHeight = args.safeHeight ?? 10
  useAutoHeight(container, safeHeight)

  return (
    <div ref={container}>{crouter.render(args.comp, null, args.props)}</div>
  )
}

export const StApp = withStreamlitConnection(App)
