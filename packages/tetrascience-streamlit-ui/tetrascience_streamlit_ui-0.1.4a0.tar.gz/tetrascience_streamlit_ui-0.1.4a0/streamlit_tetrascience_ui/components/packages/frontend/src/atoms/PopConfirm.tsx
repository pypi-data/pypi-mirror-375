import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { PopConfirm, PopConfirmProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StPopConfirm({ args, theme }: ComponentProps<any>): ReactElement {
  const {
    name,
    title = "Are you sure?",
    description = "This action cannot be undone.",
    onConfirm,
    onCancel,
    okText = "OK",
    cancelText = "Cancel",
    placement = "top",
    children = <button>Click me</button>,
    className,
    okButtonProps,
    cancelButtonProps,
    ...popConfirmProps
  } = args as {
    name?: string
    title?: React.ReactNode
    description?: React.ReactNode
    onConfirm?: (e?: React.MouseEvent<HTMLElement>) => void
    onCancel?: (e?: React.MouseEvent<HTMLElement>) => void
    okText?: string
    cancelText?: string
    placement?:
      | "top"
      | "left"
      | "right"
      | "bottom"
      | "topLeft"
      | "topRight"
      | "bottomLeft"
      | "bottomRight"
      | "leftTop"
      | "leftBottom"
      | "rightTop"
      | "rightBottom"
    children?: React.ReactNode
    className?: string
    okButtonProps?: React.ButtonHTMLAttributes<HTMLButtonElement>
    cancelButtonProps?: React.ButtonHTMLAttributes<HTMLButtonElement>
  } & Partial<PopConfirmProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Handle confirm events and send data back to Streamlit
  const handleConfirm = (e?: React.MouseEvent<HTMLElement>) => {
    if (onConfirm) {
      onConfirm(e)
    }
    // Send confirm event back to Streamlit
    Streamlit.setComponentValue({ event: "confirm", name, action: "confirm" })
  }

  const handleCancel = (e?: React.MouseEvent<HTMLElement>) => {
    if (onCancel) {
      onCancel(e)
    }
    // Send cancel event back to Streamlit
    Streamlit.setComponentValue({ event: "cancel", name, action: "cancel" })
  }

  // Merge PopConfirm props
  const mergedPopConfirmProps = {
    title,
    description,
    onConfirm: handleConfirm,
    onCancel: handleCancel,
    okText,
    cancelText,
    placement,
    children,
    className,
    okButtonProps,
    cancelButtonProps,
    ...popConfirmProps,
  }

  return <PopConfirm {...mergedPopConfirmProps} />
}

export default withStreamlitConnection(StPopConfirm)
