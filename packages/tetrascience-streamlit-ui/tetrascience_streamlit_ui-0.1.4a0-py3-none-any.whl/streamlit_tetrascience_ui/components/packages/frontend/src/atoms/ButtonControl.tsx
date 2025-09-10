import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { ButtonControl, ButtonControlProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StButtonControl({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    icon,
    selected = false,
    ...buttonControlProps
  } = args as {
    name?: string
    icon?: React.ReactNode
    selected?: ButtonControlProps["selected"]
  } & Partial<ButtonControlProps>

  // setFrameHeight should be called on first render and evertime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Handle click to send value back to Streamlit
  const handleClick = () => {
    Streamlit.setComponentValue(name || "button_control_clicked")
  }

  // Merge button control props
  const mergedButtonControlProps = {
    icon,
    selected,
    ...buttonControlProps,
    disabled: disabled || buttonControlProps.disabled,
    onClick: handleClick,
  }

  return <ButtonControl {...mergedButtonControlProps} />
}

export default withStreamlitConnection(StButtonControl)
