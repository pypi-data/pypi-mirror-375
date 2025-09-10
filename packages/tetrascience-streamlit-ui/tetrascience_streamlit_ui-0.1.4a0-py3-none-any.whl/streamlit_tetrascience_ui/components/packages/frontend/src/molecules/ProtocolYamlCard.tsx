import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { ProtocolYamlCard, ProtocolYamlCardProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StProtocolYamlCard({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    title = "Protocol Editor",
    newVersionMode = false,
    onToggleNewVersionMode,
    versionOptions = [],
    selectedVersion = "",
    onVersionChange,
    onDeploy,
    yaml = "",
    onYamlChange,
    ...protocolYamlCardProps
  } = args as {
    name?: string
    title?: string
    newVersionMode?: boolean
    onToggleNewVersionMode?: (checked: boolean) => void
    versionOptions?: Array<{ label: string; value: string }>
    selectedVersion?: string
    onVersionChange?: (value: string) => void
    onDeploy?: () => void
    yaml?: string
    onYamlChange?: (value: string) => void
  } & Partial<ProtocolYamlCardProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Handle toggle new version mode events and send data back to Streamlit
  const handleToggleNewVersionMode = (checked: boolean) => {
    if (onToggleNewVersionMode) {
      onToggleNewVersionMode(checked)
    }
    // Send toggle event back to Streamlit
    Streamlit.setComponentValue({
      event: "toggleNewVersionMode",
      name,
      newVersionMode: checked,
    })
  }

  // Handle version change events and send data back to Streamlit
  const handleVersionChange = (value: string) => {
    if (onVersionChange) {
      onVersionChange(value)
    }
    // Send version change event back to Streamlit
    Streamlit.setComponentValue({
      event: "versionChange",
      name,
      selectedVersion: value,
    })
  }

  // Handle deploy events and send data back to Streamlit
  const handleDeploy = () => {
    if (onDeploy) {
      onDeploy()
    }
    // Send deploy event back to Streamlit
    Streamlit.setComponentValue({
      event: "deploy",
      name,
      yaml,
      selectedVersion,
    })
  }

  // Handle YAML change events and send data back to Streamlit
  const handleYamlChange = (value: string) => {
    if (onYamlChange) {
      onYamlChange(value)
    }
    // Send YAML change event back to Streamlit
    Streamlit.setComponentValue({
      event: "yamlChange",
      name,
      yaml: value,
    })
  }

  // Merge protocol yaml card props
  const mergedProtocolYamlCardProps = {
    title,
    newVersionMode,
    onToggleNewVersionMode: handleToggleNewVersionMode,
    versionOptions,
    selectedVersion,
    onVersionChange: handleVersionChange,
    onDeploy: handleDeploy,
    yaml,
    onYamlChange: handleYamlChange,
    ...protocolYamlCardProps,
  }

  return <ProtocolYamlCard {...mergedProtocolYamlCardProps} />
}

export default withStreamlitConnection(StProtocolYamlCard)
