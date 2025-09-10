import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Tooltip, TooltipProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StTooltip({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    content = "This is a tooltip",
    children = <span>Hover me</span>,
    placement = "top",
    className,
    delay = 100,
    ...tooltipProps
  } = args as {
    name?: string
    content?: React.ReactNode
    children?: React.ReactNode
    placement?: "top" | "right" | "bottom" | "left"
    className?: string
    delay?: number
  } & Partial<TooltipProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Send tooltip interaction events back to Streamlit when component mounts
  useEffect(() => {
    Streamlit.setComponentValue({
      event: "mount",
      name,
      content: typeof content === "string" ? content : "tooltip content",
      placement,
    })
  }, [name, content, placement])

  // Merge tooltip props
  const mergedTooltipProps = {
    content,
    children,
    placement,
    className,
    delay,
    ...tooltipProps,
  }

  return <Tooltip {...mergedTooltipProps} />
}

export default withStreamlitConnection(StTooltip)
