import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Checkbox, CheckboxProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StCheckbox({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    checked = false,
    label = "Checkbox",
    className,
    noPadding = false,
    onClick,
    ...checkboxProps
  } = args as {
    name?: string
    checked?: boolean
    label?: React.ReactNode
    className?: string
    noPadding?: boolean
    onClick?: (e: React.MouseEvent) => void
  } & Partial<CheckboxProps>

  // Handle checkbox changes and send back to Streamlit
  const handleChange = (checkedValue: boolean) => {
    Streamlit.setComponentValue({
      checked: checkedValue,
      name: name || "checkbox",
    })
  }

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge checkbox props
  const mergedCheckboxProps = {
    checked,
    onChange: handleChange,
    label,
    className,
    noPadding,
    onClick,
    disabled: disabled || checkboxProps.disabled,
    ...checkboxProps,
  }

  return <Checkbox {...mergedCheckboxProps} />
}

export default withStreamlitConnection(StCheckbox)
