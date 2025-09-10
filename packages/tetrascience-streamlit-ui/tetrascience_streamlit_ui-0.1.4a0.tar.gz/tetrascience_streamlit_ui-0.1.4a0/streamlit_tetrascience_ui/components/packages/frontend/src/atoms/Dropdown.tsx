import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Dropdown, DropdownProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StDropdown({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    options = [],
    value,
    placeholder = "Select an option...",
    error = false,
    size = "small",
    onOpen,
    onClose,
    width,
    menuWidth,
    ...dropdownProps
  } = args as {
    name?: string
    options?: DropdownProps["options"]
    value?: string
    placeholder?: string
    error?: boolean
    size?: DropdownProps["size"]
    onOpen?: () => void
    onClose?: () => void
    width?: string
    menuWidth?: string
  } & Partial<DropdownProps>

  // Handle selection changes and send back to Streamlit
  const handleChange = (selectedValue: string) => {
    Streamlit.setComponentValue({
      value: selectedValue,
      name: name || "dropdown",
    })
  }

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge dropdown props
  const mergedDropdownProps = {
    options,
    value,
    placeholder,
    error,
    size,
    onChange: handleChange,
    onOpen,
    onClose,
    width,
    menuWidth,
    disabled: disabled || dropdownProps.disabled,
    ...dropdownProps,
  }

  return <Dropdown {...mergedDropdownProps} />
}

export default withStreamlitConnection(StDropdown)
