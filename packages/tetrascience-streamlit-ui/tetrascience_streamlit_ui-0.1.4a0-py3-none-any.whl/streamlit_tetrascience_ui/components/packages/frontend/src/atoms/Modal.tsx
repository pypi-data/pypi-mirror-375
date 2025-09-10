import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Modal, ModalProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StModal({ args, theme }: ComponentProps<any>): ReactElement {
  const {
    name,
    isOpen = false,
    onClose,
    onCloseLabel = "Cancel",
    onConfirm,
    onConfirmLabel = "Confirm",
    children = <p>This is modal content.</p>,
    width = "400px",
    className,
    hideActions = false,
    title = "Modal Title",
    ...modalProps
  } = args as {
    name?: string
    isOpen?: boolean
    onClose?: () => void
    onCloseLabel?: string
    onConfirm?: () => void
    onConfirmLabel?: string
    children?: React.ReactNode
    width?: string
    className?: string
    hideActions?: boolean
    title?: string
  } & Partial<ModalProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Handle close events and send data back to Streamlit
  const handleClose = () => {
    if (onClose) {
      onClose()
    }
    // Send close event back to Streamlit
    Streamlit.setComponentValue({ event: "close", name, action: "close" })
  }

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm()
    }
    // Send confirm event back to Streamlit
    Streamlit.setComponentValue({ event: "confirm", name, action: "confirm" })
  }

  // Merge modal props
  const mergedModalProps = {
    isOpen,
    onClose: handleClose,
    onCloseLabel,
    onConfirm: handleConfirm,
    onConfirmLabel,
    children,
    width,
    className,
    hideActions,
    title,
    ...modalProps,
  }

  return <Modal {...mergedModalProps} />
}

export default withStreamlitConnection(StModal)
