import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { MenuItem, MenuItemProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StMenuItem({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    label = "Menu Item",
    checked = false,
    showCheckbox = false,
    onClick,
    onCheckChange,
    active = false,
    className,
    ...menuItemProps
  } = args as {
    name?: string
    label?: string
    checked?: boolean
    showCheckbox?: boolean
    onClick?: () => void
    onCheckChange?: (checked: boolean) => void
    active?: boolean
    className?: string
  } & Partial<MenuItemProps>

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
    Streamlit.setComponentValue({ event: "click", name, label })
  }

  const handleCheckChange = (isChecked: boolean) => {
    if (onCheckChange) {
      onCheckChange(isChecked)
    }
    // Send check change event back to Streamlit
    Streamlit.setComponentValue({
      event: "check_change",
      name,
      label,
      checked: isChecked,
    })
  }

  // Merge menu item props
  const mergedMenuItemProps = {
    label,
    checked,
    showCheckbox,
    onClick: handleClick,
    onCheckChange: handleCheckChange,
    active,
    className,
    ...menuItemProps,
  }

  return <MenuItem {...mergedMenuItemProps} />
}

export default withStreamlitConnection(StMenuItem)
