import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Toggle, ToggleProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StToggle({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    checked = false,
    onChange,
    label,
    className,
    ...toggleProps
  } = args as {
    name?: string
    checked?: boolean
    onChange?: (checked: boolean) => void
    disabled?: boolean
    label?: string
    className?: string
  } & Partial<ToggleProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Handle toggle change events and send data back to Streamlit
  const handleChange = (isChecked: boolean) => {
    if (onChange) {
      onChange(isChecked)
    }
    // Send change event back to Streamlit
    Streamlit.setComponentValue({
      event: "change",
      name,
      checked: isChecked,
      label,
    })
  }

  // Merge toggle props
  const mergedToggleProps = {
    checked,
    onChange: handleChange,
    disabled,
    label,
    className,
    ...toggleProps,
  }

  return <Toggle {...mergedToggleProps} />
}

export default withStreamlitConnection(StToggle)
