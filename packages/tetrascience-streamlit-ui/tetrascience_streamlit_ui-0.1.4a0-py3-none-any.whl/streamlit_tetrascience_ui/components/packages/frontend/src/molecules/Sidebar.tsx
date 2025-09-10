import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Sidebar, SidebarProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StSidebar({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    items = [],
    activeItem,
    ...sidebarProps
  } = args as {
    items?: Array<{
      icon: string
      label: string
      active?: boolean
    }>
    activeItem?: string
  } & Partial<SidebarProps>

  useEffect(() => {
    // Calculate exact height: 70px per item, no extra padding
    const exactHeight = items.length * 70
    Streamlit.setFrameHeight(exactHeight)
  }, [theme, items])

  const handleItemClick = (label: string) => {
    Streamlit.setComponentValue({
      event: "item_click",
      label: label,
      timestamp: new Date().toISOString(),
    })
  }

  const mergedSidebarProps = {
    items: items.map((item) => ({
      icon: item.icon as any,
      label: item.label,
      active: item.active,
    })),
    activeItem,
    onItemClick: handleItemClick,
    ...sidebarProps,
  }

  return <Sidebar {...mergedSidebarProps} />
}

export default withStreamlitConnection(StSidebar)
