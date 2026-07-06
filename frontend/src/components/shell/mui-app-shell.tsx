"use client";

import {
  AppBar,
  Avatar,
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Stack,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  ChevronLeft,
  ChevronRight,
  DarkMode,
  LightMode,
  Menu as MenuIcon,
  NotificationsNone,
  Search,
} from "@mui/icons-material";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme as useNextTheme } from "next-themes";
import { useEffect, useState, type ReactNode } from "react";
import {
  filterNavByRole,
  NAV_SECTIONS,
  PLACEHOLDER_USER_ROLE,
} from "@/constants/nav-config";
import { ROUTES, SITE_NAME } from "@/constants/routes";
import { DRAWER_WIDTH, DRAWER_WIDTH_COLLAPSED } from "@/theme/material-theme";
import { useUiStore } from "@/stores/ui-store";

interface MuiAppShellProps {
  children: ReactNode;
}

export function MuiAppShell({ children }: MuiAppShellProps) {
  const pathname = usePathname();
  const muiTheme = useTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down("md"));
  const collapsed = useUiStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useUiStore((s) => s.toggleSidebar);
  const { resolvedTheme, setTheme } = useNextTheme();
  const [mounted, setMounted] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);

  useEffect(() => setMounted(true), []);

  const drawerWidth = collapsed && !isMobile ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH;
  const navSections = filterNavByRole(NAV_SECTIONS, PLACEHOLDER_USER_ROLE);

  const drawerContent = (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <Toolbar
        sx={{
          gap: 1.5,
          minHeight: 64,
          px: collapsed && !isMobile ? 1 : 2,
          justifyContent: collapsed && !isMobile ? "center" : "flex-start",
        }}
      >
        <Avatar
          sx={{
            width: 36,
            height: 36,
            bgcolor: "primary.main",
            fontSize: 14,
            fontWeight: 700,
          }}
        >
          KF
        </Avatar>
        {(!collapsed || isMobile) && (
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="subtitle1" noWrap fontWeight={600}>
              {SITE_NAME}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              Bhairkhanpally
            </Typography>
          </Box>
        )}
      </Toolbar>

      <Divider />

      <Box sx={{ flex: 1, overflowY: "auto", py: 1 }}>
        {navSections.map((section) => (
          <Box key={section.title} sx={{ mb: 1.5 }}>
            {(!collapsed || isMobile) && (
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{
                  px: 2.5,
                  py: 0.5,
                  display: "block",
                  fontWeight: 600,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                }}
              >
                {section.title}
              </Typography>
            )}
            <List dense disablePadding>
              {section.items.map((item) => {
                const active =
                  pathname === item.href || pathname.startsWith(`${item.href}/`);
                const Icon = item.icon;
                return (
                  <ListItem key={item.href} disablePadding sx={{ px: 0.5 }}>
                    <ListItemButton
                      component={Link}
                      href={item.href}
                      selected={active}
                      onClick={() => isMobile && setMobileOpen(false)}
                      sx={{
                        justifyContent: collapsed && !isMobile ? "center" : "flex-start",
                        px: collapsed && !isMobile ? 1 : 2,
                        minHeight: 44,
                      }}
                    >
                      <ListItemIcon
                        sx={{
                          minWidth: collapsed && !isMobile ? 0 : 40,
                          justifyContent: "center",
                          color: active ? "primary.main" : "text.secondary",
                        }}
                      >
                        <Icon fontSize="small" />
                      </ListItemIcon>
                      {(!collapsed || isMobile) && (
                        <ListItemText
                          primary={item.label}
                          primaryTypographyProps={{
                            fontSize: 14,
                            fontWeight: active ? 600 : 500,
                          }}
                        />
                      )}
                    </ListItemButton>
                  </ListItem>
                );
              })}
            </List>
          </Box>
        ))}
      </Box>

      {!isMobile && (
        <>
          <Divider />
          <Box sx={{ p: 1 }}>
            <Tooltip title={collapsed ? "Expand sidebar" : "Collapse sidebar"}>
              <IconButton onClick={toggleSidebar} sx={{ width: "100%", borderRadius: 2 }}>
                {collapsed ? <ChevronRight /> : <ChevronLeft />}
              </IconButton>
            </Tooltip>
          </Box>
        </>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBar
        position="fixed"
        color="inherit"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          bgcolor: "background.paper",
        }}
      >
        <Toolbar sx={{ gap: 1, minHeight: 64 }}>
          {isMobile && (
            <IconButton edge="start" onClick={() => setMobileOpen(true)} aria-label="Open menu">
              <MenuIcon />
            </IconButton>
          )}

          <Box
            sx={{
              display: { xs: "none", lg: "flex" },
              alignItems: "center",
              gap: 1,
              px: 1.5,
              py: 0.75,
              borderRadius: 2,
              bgcolor: "action.hover",
              flex: 1,
              maxWidth: 420,
            }}
          >
            <Search fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Search farmers, procurements…
            </Typography>
          </Box>

          <Stack direction="row" spacing={0.5} sx={{ ml: "auto" }}>
            <IconButton aria-label="Notifications">
              <NotificationsNone />
            </IconButton>
            {mounted && (
              <IconButton
                aria-label="Toggle theme"
                onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
              >
                {resolvedTheme === "dark" ? <LightMode /> : <DarkMode />}
              </IconButton>
            )}
            <IconButton onClick={(e) => setUserMenuAnchor(e.currentTarget)}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: "primary.main", fontSize: 13 }}>
                VG
              </Avatar>
            </IconButton>
          </Stack>
        </Toolbar>
      </AppBar>

      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={() => setUserMenuAnchor(null)}
      >
        <MenuItem disabled>
          <Stack>
            <Typography variant="body2" fontWeight={600}>
              Venkat Gorinta
            </Typography>
            <Typography variant="caption" color="text.secondary">
              owner@krishifarms.local
            </Typography>
          </Stack>
        </MenuItem>
        <Divider />
        <MenuItem component={Link} href={ROUTES.settings} onClick={() => setUserMenuAnchor(null)}>
          Settings
        </MenuItem>
      </Menu>

      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={isMobile ? mobileOpen : true}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            "& .MuiDrawer-paper": {
              width: drawerWidth,
              boxSizing: "border-box",
              transition: muiTheme.transitions.create("width", {
                easing: muiTheme.transitions.easing.sharp,
                duration: muiTheme.transitions.duration.enteringScreen,
              }),
              overflowX: "hidden",
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          pt: "64px",
          minHeight: "100vh",
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
