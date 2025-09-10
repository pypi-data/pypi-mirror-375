import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Badge, BadgeProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StBadge({ args, disabled, theme }: ComponentProps<any>): ReactElement {
  const {
    name,
    label = "Badge",
    variant = "primary",
    size = "small",
    ...badgeProps
  } = args as {
    name?: string
    label?: string
    variant?: BadgeProps["variant"]
    size?: BadgeProps["size"]
  } & Partial<BadgeProps>

  // setFrameHeight should be called on first render and evertime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge badge props
  const mergedBadgeProps = {
    variant,
    size,
    ...badgeProps,
    disabled: disabled || badgeProps.disabled,
  }

  return <Badge {...mergedBadgeProps}>{label}</Badge>
}

export default withStreamlitConnection(StBadge)
