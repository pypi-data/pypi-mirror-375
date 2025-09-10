import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Toast, ToastProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StToast({ args, disabled, theme }: ComponentProps<any>): ReactElement {
  const {
    name,
    type = "default",
    heading = "Toast Notification",
    description,
    className,
    ...toastProps
  } = args as {
    name?: string
    type?: "info" | "success" | "warning" | "danger" | "default"
    heading?: string
    description?: string
    className?: string
  } & Partial<ToastProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Send toast display event back to Streamlit when component mounts
  useEffect(() => {
    Streamlit.setComponentValue({
      event: "display",
      name,
      type,
      heading,
      description,
    })
  }, [name, type, heading, description])

  // Merge toast props
  const mergedToastProps = {
    type,
    heading,
    description,
    className,
    ...toastProps,
  }

  return <Toast {...mergedToastProps} />
}

export default withStreamlitConnection(StToast)
