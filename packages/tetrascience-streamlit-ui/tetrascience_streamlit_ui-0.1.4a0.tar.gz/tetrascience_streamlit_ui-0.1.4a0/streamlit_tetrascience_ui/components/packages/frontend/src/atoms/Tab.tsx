import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Tab, TabProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StTab({ args, disabled, theme }: ComponentProps<any>): ReactElement {
  const {
    name,
    label = "Tab Label",
    active = false,
    size = "medium",
    onClick,
    ...tabProps
  } = args as {
    name?: string
    label?: string
    active?: boolean
    disabled?: boolean
    size?: "small" | "medium"
    onClick?: () => void
  } & Partial<TabProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Handle click events and send data back to Streamlit
  const handleClick = () => {
    if (onClick) {
      onClick()
    }
    // Send click event back to Streamlit
    Streamlit.setComponentValue({ event: "click", name, label, active })
  }

  // Merge tab props
  const mergedTabProps = {
    label,
    active,
    disabled,
    size,
    onClick: handleClick,
    ...tabProps,
  }

  return <Tab {...mergedTabProps} />
}

export default withStreamlitConnection(StTab)
